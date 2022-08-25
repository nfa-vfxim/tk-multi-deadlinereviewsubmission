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
from shutil import rmtree
from subprocess import check_output

# standard toolkit logger
logger = sgtk.platform.get_logger(__name__)


class DeadlineReviewSubmissionHandler:
    def __init__(self):
        self.__app = sgtk.platform.current_bundle()
        self.deadline_command = os.getenv("DEADLINE_PATH")

    def submit_to_deadline(
        self,
        template,
        fields,
        sg_publishes,
        start_frame,
        end_frame,
        fps,
        filename,
        comment=None,
    ):
        """Get parameters from publisher, translate them to text and
        submit using deadline command

        Args:
            template (attribute): publisher template
            fields (attribute): fields from render path
            sg_publishes (list): data created by publisher
            start_frame (int): first frame for sequence
            end_frame (_type_): last frame for sequence
            fps (int): frames per second used in project
            filename (str): script name current file
            comment (str, optional): any comment made by artist.
            Defaults to None.
        """
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

            # Getting settings from the app configuration
            priority = self.__app.get_setting("default_priority")
            company_name = self.__app.get_setting("company_name")

            render_path = self.__app.get_template("review_output_path")
            render_path = render_path.apply_fields(fields)

            if comment is None:
                comment = " "

            department = "ShotGrid"
            plugin = "ShotGridReview"

            # Every argument has to be split because we are
            # sending it via deadlinecommand
            submission_parameters = self.__get_submission_parameters(
                plugin=plugin,
                priority=priority,
                department=department,
                filename=filename,
                start_frame=start_frame,
                end_frame=end_frame,
                fps=fps,
                project_id=project_id,
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                publish_id=publish_id,
                task_id=task_id,
                sequence_path=sequence_path,
                render_path=render_path,
                company_name=company_name,
                project_name=project_name,
                user_name=user_name,
                comment=comment,
                entity_version=entity_version,
            )

            # Submit to Deadline
            self.__submit_to_deadline(submission_parameters)

            return render_path

    def __get_submission_parameters(
        self,
        plugin,
        priority,
        department,
        filename,
        start_frame,
        end_frame,
        fps,
        project_id,
        user_id,
        entity_type,
        entity_id,
        publish_id,
        task_id,
        sequence_path,
        render_path,
        company_name,
        project_name,
        user_name,
        comment,
        entity_version,
    ):
        """
        Create dictionaries containing all submission parameters
        the panel gives.
        Will return a dictionary:
            {
            "job_info": {
                "Plugin": "Nuke",
                "Frames": "1-100",
                "Priority": 70,
                "Name": "ExampleScript",
                "Department": "Compositing",
                "ConcurrentTasks": 10,
                "ChunkSize": 3,
                "OutputDirectory0": "/example/path",
                "OutputFilename0": "file.exr",
            },
            "plugin_info": {
                "Version": "13.2",
                "WriteNode": "Write1",
                "SceneFile": "/example/path/ExampleScript.nk",
            },
        }
        """

        # Getting job submission parameters
        job_info = {}
        job_info["Plugin"] = plugin
        job_info["Priority"] = priority
        job_info["Name"] = filename
        job_info["Department"] = department
        job_info["OutputDirectory0"] = os.path.dirname(render_path)
        job_info["OutputFilename0"] = os.path.basename(render_path)

        # Getting plugin submission parameters
        plugin_info = {}
        plugin_info["Version"] = 1
        plugin_info["StartFrame"] = start_frame
        plugin_info["EndFrame"] = end_frame
        plugin_info["FPS"] = fps
        plugin_info["ProjectID"] = project_id
        plugin_info["UserID"] = user_id
        plugin_info["EntityType"] = entity_type
        plugin_info["PublishID"] = publish_id
        plugin_info["TaskID"] = task_id
        plugin_info["SequenceFile"] = sequence_path
        plugin_info["OutputFile"] = render_path
        plugin_info["CompanyName"] = company_name
        plugin_info["ProjectName"] = project_name
        plugin_info["Artist"] = user_name
        plugin_info["Description"] = comment
        plugin_info["ShotGridVersion"] = entity_version
        plugin_info["FileName"] = filename

        # Create dictionary containing both dictionaries
        submission_files = {
            "job_info": job_info,
            "plugin_info": plugin_info,
        }

        return submission_files

    def __submit_to_deadline(self, submission_parameters):
        """
        This function will create using the provided submission
        dictionary both the job_info.txt file and plugin_info.txt.
        This will be done in a temporary directory.
        After the creation of these files, we call the deadlinecommand
        and submit the job to Deadline.
        """

        # First we will create the necessary files to submit
        # These are the job_info.txt and plugin_info.txt
        # After submitting these files Deadline will understand the submission

        submission_files = []

        # Setting initial message in case something went wrong
        # We will change this variable if submission succeeded
        result = "Something went wrong"

        # Create temporary directory for submission text files
        temporary_directory = tempfile.mkdtemp()

        # We run the code within a try and except to
        # catch any exceptions and give them to the user
        try:

            # Iterating through the provided dictionary, and get
            # the created dictionaries inside.
            for submission_info in submission_parameters.keys():

                # Get the parameters for the specified dictionary
                # (for example job_info)
                info_parameters = submission_parameters.get(submission_info)

                # Create the path for the info_file.txt, for example
                # path/to/temporarydirectory/job_info.txt
                info_file = os.path.join(
                    temporary_directory,
                    submission_info + ".txt",
                )

                # Fix for Windows backward slashes systems
                info_file = info_file.replace(os.sep, "/")

                # Create a text file
                info_file_txt = open(info_file, "w", encoding="utf-8")

                # Iterate through the dictionary for every key
                for parameter in info_parameters.keys():

                    # Get the value per parameter
                    value = info_parameters.get(parameter)

                    # Write the key and value and create a new line
                    # For example:
                    # Plugin=Nuke (key=value)
                    info_file_txt.write(parameter + "=" + str(value) + "\n")

                # Close the file to write parameters
                info_file_txt.close()

                # Add the created text file to the list for submission
                submission_files.append(info_file)

            # Create the command for calling deadline
            deadline_command = [
                os.path.join(self.deadline_command, "deadlinecommand")
            ]

            # Append the text files for the submission parameters
            deadline_command = deadline_command + submission_files

            # Create a subprocess using deadlinecommand and run the submission
            submission = check_output(deadline_command)

            # Return the command output so the user
            # will get the submission information
            result = str(submission)

        # If there is an error, return the error
        # so the user knows
        except Exception as error:
            result = str(error)

        # Always remove the created temporary directory
        finally:
            rmtree(temporary_directory)

        return result
