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
import os
import tempfile
from subprocess import check_output

# standard toolkit logger
logger = sgtk.platform.get_logger(__name__)


class DeadlineReviewSubmissionHandler:
    def __init__(self):
        self.__app = sgtk.platform.current_bundle()

    def submit_to_deadline(
        self,
        template=None,
        fields=None,
        sg_publishes=None,
        start_frame=None,
        end_frame=None,
        fps=None,
        filename=None,
        comment=None,
    ):

        ### Getting attached data from the publish plugin
        # Building template to get sequence path
        fields["SEQ"] = "FORMAT: %d"
        sequence_path = template.apply_fields(fields)
        for publish in sg_publishes:
            # Getting current project id and project name
            project_id = publish.get("project").get("id")
            project_name = publish.get("project").get("name")

            # Getting entity data
            entity_version = publish.get("version_number")
            entity_id = publish.get("entity").get("id")
            entity_type = publish.get("entity").get("type")

            # Getting task id
            task_id = publish.get("task").get("id")

            # Getting info about the submitter
            user_name = publish.get("created_by").get("name")
            user_id = publish.get("created_by").get("id")

            # Getting publish id
            publish_id = publish.get("id")

            ### Getting settings from the app configuration
            priority = self.__app.get_setting("default_priority")
            company_name = self.__app.get_setting("company_name")

            render_path = self.__app.get_template("review_output_path")
            render_path = render_path.apply_fields(fields)

            if comment is None:
                comment = " "

            ### Getting system data
            # Location of deadline installation
            deadline_path = os.getenv("DEADLINE_PATH")

            ### Building all files
            # Building job info properties
            job_info = [
                "Name=" + filename,
                "Plugin=ShotGridReview",
                "Department=ShotGrid",
                "Priority=" + str(priority),
            ]

            # Building plugin info properties
            plugin_info = [
                "Version=1",
                "StartFrame=" + str(start_frame),
                "EndFrame=" + str(end_frame),
                "FPS=" + str(fps),
                "ProjectID=" + str(project_id),
                "UserID=" + str(user_id),
                "EntityType=" + entity_type,
                "EntityID=" + str(entity_id),
                "PublishID=" + str(publish_id),
                "TaskID=" + str(task_id),
                "SequenceFile=" + sequence_path,
                "OutputFile=" + render_path,
                "CompanyName=" + company_name,
                "ProjectName=" + project_name,
                "Artist=" + user_name,
                "Description=" + comment,
                "ShotGridVersion=" + str(entity_version),
                "FileName=" + filename,
            ]

            # Create temporary directory to create job info and plugin files for submission
            temporary_directory = tempfile.mkdtemp()

            # Writing job_info.txt
            job_info_filepath = os.path.join(
                temporary_directory, "job_info.txt"
            ).replace(os.sep, "/")
            job_info_textfile = open(job_info_filepath, "w")
            for item in job_info:
                job_info_textfile.write(item + "\n")
            job_info_textfile.close()

            # Writing plugin_info.txt
            plugin_info_filepath = os.path.join(
                temporary_directory, "plugin_info.txt"
            ).replace(os.sep, "/")
            plugin_info_textfile = open(plugin_info_filepath, "w")
            for item in plugin_info:
                plugin_info_textfile.write(item + "\n")
            plugin_info_textfile.close()

            deadline_command = [
                os.path.join(deadline_path, "deadlinecommand"),
                job_info_filepath,
                plugin_info_filepath,
            ]

            execute_submission = check_output(deadline_command)

            return render_path
