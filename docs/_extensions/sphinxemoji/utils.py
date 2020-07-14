import json
from urllib.request import urlopen


def get_gemojione():
    remote = 'https://raw.githubusercontent.com/bonusly/gemojione/master'
    data = json.load(urlopen(remote + '/config/index.json'))
    codes = {}
    for emoji in data.values():
        codes[emoji['shortname']] = emoji['moji']
        for alias in emoji['aliases']:
            codes[alias] = emoji['moji']
    return codes


def get_joypixels():
    remote = 'https://raw.githubusercontent.com/joypixels/emoji-toolkit/master'
    data = json.load(urlopen(remote + '/emoji.json'))
    codes = {}
    for info in data.values():
        hexstring = info['code_points']['fully_qualified']
        emoji = ''.join(chr(int(c, 16)) for c in hexstring.split('-'))
        codes[info['shortname']] = emoji
        for alias in info['shortname_alternates']:
            codes[alias] = emoji
    return codes


def update_codes():
    with open('sphinxemoji/codes.json') as current:
        codes = json.load(current)
    for getter in [
        get_gemojione,
        get_joypixels,
    ]:
        codes.update(getter())
    with open('sphinxemoji/codes.json', 'w') as output:
        json.dump(codes, output, sort_keys=True, indent=4, ensure_ascii=False)
        output.write('\n')


if __name__ == '__main__':
    update_codes()
