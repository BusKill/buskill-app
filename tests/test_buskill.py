"""
tests/test_buskill.py

Unit tests for BusKill core logic that do NOT require USB hardware.

Run with:
    cd buskill-app
    pytest tests/test_buskill.py -v

Related issues: https://github.com/BusKill/buskill-app/issues/32
"""

import os, sys, hashlib, tempfile, platform, logging
import pytest

# ---------------------------------------------------------------------------
# Make src/ and src/packages/ importable
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR   = os.path.join(REPO_ROOT, 'src')
PKG_DIR   = os.path.join(SRC_DIR, 'packages')
for p in (SRC_DIR, PKG_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------------------------
# Fix: BusKill.__init__ calls logger.root.handlers[0].baseFilename, but
# pytest replaces the root handlers with its own _LiveLoggingNullHandler
# which has no baseFilename. We inject a real FileHandler before importing
# so the attribute is always present.
# ---------------------------------------------------------------------------
_tmp_log = os.path.join(tempfile.gettempdir(), 'buskill_test.log')
_fh = logging.FileHandler(_tmp_log)
logging.root.handlers.insert(0, _fh)

from buskill import BusKill


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def make_buskill():
    return BusKill()


# ---------------------------------------------------------------------------
# 1. Platform Detection
# ---------------------------------------------------------------------------
class TestPlatformDetection:

    def test_current_platform_is_set(self):
        bk = make_buskill()
        assert bk.CURRENT_PLATFORM is not None
        assert len(bk.CURRENT_PLATFORM) > 0

    def test_os_name_short_is_set(self):
        bk = make_buskill()
        assert bk.OS_NAME_SHORT in ('lin', 'win', 'mac')

    def test_is_platform_supported_returns_bool(self):
        bk = make_buskill()
        assert isinstance(bk.is_platform_supported(), bool)

    def test_supported_platforms_are_recognised(self):
        bk = make_buskill()
        for short in ('lin', 'win', 'mac'):
            bk.OS_NAME_SHORT = short
            assert bk.is_platform_supported() is True

    def test_unsupported_platform_returns_false(self):
        bk = make_buskill()
        bk.OS_NAME_SHORT = 'bsd'
        assert bk.is_platform_supported() is False

    def test_err_message_contains_platform_name(self):
        bk = make_buskill()
        assert platform.system() in bk.ERR_PLATFORM_NOT_SUPPORTED


# ---------------------------------------------------------------------------
# 2. Supported Triggers List
# ---------------------------------------------------------------------------
class TestSupportedTriggers:

    def test_supported_triggers_is_list(self):
        assert isinstance(make_buskill().SUPPORTED_TRIGGERS, list)

    def test_lock_screen_present(self):
        assert 'lock-screen' in make_buskill().SUPPORTED_TRIGGERS

    def test_soft_shutdown_present(self):
        assert 'soft-shutdown' in make_buskill().SUPPORTED_TRIGGERS

    def test_at_least_two_triggers(self):
        assert len(make_buskill().SUPPORTED_TRIGGERS) >= 2


# ---------------------------------------------------------------------------
# 3. set_trigger / get_trigger
# ---------------------------------------------------------------------------
class TestSetGetTrigger:

    def test_trigger_none_on_init(self):
        assert make_buskill().trigger is None

    def test_set_lock_screen(self):
        bk = make_buskill()
        bk.set_trigger('lock-screen')
        assert bk.get_trigger() == 'lock-screen'

    def test_set_soft_shutdown(self):
        bk = make_buskill()
        bk.set_trigger('soft-shutdown')
        assert bk.get_trigger() == 'soft-shutdown'

    def test_invalid_trigger_raises(self):
        bk = make_buskill()
        with pytest.raises(Exception):
            bk.set_trigger('explode-computer')

    def test_get_trigger_returns_string(self):
        bk = make_buskill()
        bk.set_trigger('lock-screen')
        assert isinstance(bk.get_trigger(), str)

    def test_trigger_overwrite(self):
        bk = make_buskill()
        bk.set_trigger('lock-screen')
        bk.set_trigger('soft-shutdown')
        assert bk.get_trigger() == 'soft-shutdown'

    def test_empty_string_raises(self):
        bk = make_buskill()
        with pytest.raises(Exception):
            bk.set_trigger('')

    def test_none_raises(self):
        bk = make_buskill()
        with pytest.raises(Exception):
            bk.set_trigger(None)


# ---------------------------------------------------------------------------
# 4. integrity_is_ok (SHA-256 verification)
# ---------------------------------------------------------------------------
class TestIntegrityIsOk:

    def _make_files(self, contents: dict):
        """Write {name: bytes}, return (sums_path, [file_paths])."""
        tmp = tempfile.mkdtemp()
        fps, lines = [], []
        for name, data in contents.items():
            fp = os.path.join(tmp, name)
            with open(fp, 'wb') as f:
                f.write(data)
            cksum = hashlib.sha256(data).hexdigest()
            lines.append(f"{cksum}  {name}\n")
            fps.append(fp)
        sums = os.path.join(tmp, 'SHA256SUMS')
        with open(sums, 'w') as f:
            f.writelines(lines)
        return sums, fps

    def test_single_file_passes(self):
        bk = make_buskill()
        s, fps = self._make_files({'f.bin': b'hello buskill'})
        assert bk.integrity_is_ok(s, fps) is True

    def test_multiple_files_pass(self):
        bk = make_buskill()
        s, fps = self._make_files({'a.bin': b'alpha', 'b.bin': b'beta', 'c.bin': b'gamma'})
        assert bk.integrity_is_ok(s, fps) is True

    def test_tampered_file_fails(self):
        bk = make_buskill()
        s, fps = self._make_files({'p.bin': b'original'})
        with open(fps[0], 'wb') as f:
            f.write(b'tampered!')
        assert bk.integrity_is_ok(s, fps) is False

    def test_empty_file_passes(self):
        bk = make_buskill()
        s, fps = self._make_files({'empty.bin': b''})
        assert bk.integrity_is_ok(s, fps) is True

    def test_large_file_passes(self):
        bk = make_buskill()
        s, fps = self._make_files({'big.bin': b'X' * (1024 * 1024)})
        assert bk.integrity_is_ok(s, fps) is True


# ---------------------------------------------------------------------------
# 5. setupDataDir
# ---------------------------------------------------------------------------
class TestSetupDataDir:

    def test_data_dir_set(self):
        assert make_buskill().DATA_DIR is not None

    def test_cache_dir_under_data_dir(self):
        bk = make_buskill()
        if bk.DATA_DIR:
            assert bk.CACHE_DIR.startswith(bk.DATA_DIR)

    def test_data_dir_named_buskill(self):
        bk = make_buskill()
        if bk.DATA_DIR:
            assert bk.DATA_DIR.endswith('.buskill')


# ---------------------------------------------------------------------------
# 6. Documentation URLs
# ---------------------------------------------------------------------------
class TestDocumentationUrls:

    def test_url_website(self):
        assert make_buskill().url_website.startswith('https://')

    def test_url_docs(self):
        assert make_buskill().url_documentation.startswith('https://')

    def test_url_bug_report(self):
        url = make_buskill().url_documentation_bug_report
        assert 'github' in url or 'buskill' in url

    def test_url_contribute(self):
        assert make_buskill().url_documentation_contribute.startswith('https://')


# ---------------------------------------------------------------------------
# 7. __getstate__ (pickle safety)
# ---------------------------------------------------------------------------
class TestGetState:

    def test_returns_dict(self):
        assert isinstance(make_buskill().__getstate__(), dict)

    def test_excludes_unpickleable_fields(self):
        state = make_buskill().__getstate__()
        for field in ('upgrade_process', 'usb_handler', 'root_child'):
            assert field not in state

    def test_contains_trigger_key(self):
        assert 'trigger' in make_buskill().__getstate__()


# ---------------------------------------------------------------------------
# 8. Armed state
# ---------------------------------------------------------------------------
class TestArmedState:

    def test_is_armed_none_on_init(self):
        assert make_buskill().is_armed is None
