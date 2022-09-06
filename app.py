# MIT License

# Copyright (c) 2021 Netherlands Film Academy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sgtk


class TkDeadlineReviewSubmissionApp(sgtk.platform.Application):
    """
    The tk_multi_deadlinereviewsubmission entry point. This class is responsible for initializing and tearing down
    the application, handle menu registration etc.
    """

    def init_app(self):
        """
        Called as the application is being initialized
        """
        self.tk_multi_deadlinereviewsubmission = self.import_module(
            "tk_multi_deadlinereviewsubmission"
        )
        self.handler = (
            self.tk_multi_deadlinereviewsubmission.DeadlineReviewSubmissionHandler()
        )

    def submit_version(
        self,
        template,
        fields,
        publish,
        first_frame,
        last_frame,
        fps,
        colorspace_idt=None,
        colorspace_odt=None,
    ):

        result = self.handler.submit_to_deadline(
            template=template,
            fields=fields,
            publish=publish,
            first_frame=first_frame,
            last_frame=last_frame,
            fps=fps,
            colorspace_idt=colorspace_idt,
            colorspace_odt=colorspace_odt,
        )

        return result
