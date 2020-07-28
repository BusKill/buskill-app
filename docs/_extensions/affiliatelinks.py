"""
::

  File:    affiliatelinks.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-07-28
  Updated: 2020-07-28
  Version: 0.1

This sphinx extension takes a list of links and builds targets from those links
depending on the buildername. If the buildername is 'html', it will use our
affiliate links. Otherwise, the target will use the fallback link.

This is important because amazon affiliates don't permit offline material to
include affiliate links, so we need to make sure that our pdf, epub, etc just
link to our online documentation and not directly to our affiliate's products.

For more info, see: https://buskill.in/
"""
from docutils import nodes
from docutils.parsers.rst import Directive

from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective

class AffiliateLinks(SphinxDirective):

	has_content = True

	def run(self):

		# generate a list of targets for each line in the body passed to us
		target_nodes = list()
		for target in self.content:

			# skip empty lines
			if target == '':
				continue

			target_node = nodes.target( '', '' )
			target_nodes.append( target_node )

			# split this line up into space-separated fields
			affiliateUri,fallbackUri,name = target.split()

			# the name of the target is what it will be referenced by in .rst
			# files (eg: `some hyperlink custom text`targetname_ )
			target_node['names'] = [name]

			# only use the affiliate link if we're building html
			# use the fall-back URI if we're building to anything else, such as pdf
			if self.env.config.buildername == 'html':
				target_node['refuri'] = affiliateUri
			else:
				target_node['refuri'] = fallbackUri

		return target_nodes

def setup(app):
	app.add_directive("affiliatelinks", AffiliateLinks)

	return {
		'version': '0.1',
		'parallel_read_safe': True,
		'parallel_write_safe': True,
	}
