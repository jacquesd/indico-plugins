# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

import nbformat
from flask import session, render_template, request
from nbconvert.exporters import HTMLExporter
from traitlets.config import Config
from werkzeug.exceptions import Forbidden

from indico.modules.attachments import Attachment

from MaKaC.webinterface.rh.base import RH

from indico_previewer_jupyter.cpp_highlighter import CppHighlighter


class RHEventPreviewIPyNB(RH):
    def _checkProtection(self):
        RH._checkProtection(self)
        if not self.attachment.can_access(session.user):
            raise Forbidden

    def _checkParams(self, params):
        RH._checkParams(self, params)
        self.attachment = Attachment.find_one(id=request.view_args['attachment_id'], is_deleted=False)

    def _process(self):
        config = Config()
        config.HTMLExporter.preprocessors = [CppHighlighter]
        config.HTMLExporter.template_file = 'full'

        with self.attachment.file.open() as f:
            notebook = nbformat.read(f, as_version=4)

        html_exporter = HTMLExporter(config=config)
        body, resources = html_exporter.from_notebook_node(notebook)
        css_code = '\n'.join(resources['inlining'].get('css', []))

        return render_template('previewer_jupyter:ipynb_preview.html', attachment=self.attachment,
                               html_code=body, css_code=css_code)
