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
        publish,
        first_frame,
        last_frame,
        fps,
        colorspace_idt,
        colorspace_odt,
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

        # Getting publish id
        publish_id = publish.get("id")

        # Getting settings from the app configuration
        priority = self.__app.get_setting("default_priority")
        company = self.__app.get_setting("company_name")

        slate_path = self.__app.get_template("review_output_path")
        slate_path = slate_path.apply_fields(fields)

        if colorspace_idt is None:
            colorspace_idt = self.__app.get_setting("default_colorspace_idt")

        if colorspace_odt is None:
            colorspace_odt = self.__app.get_setting("default_colorspace_odt")

        department = "Pipeline"
        plugin = "ShotGridReview"

        # Every argument has to be split because we are
        # sending it via deadlinecommand
        submission_parameters = self.__get_submission_parameters(
            plugin=plugin,
            priority=priority,
            department=department,
            publish_id=publish_id,
            first_frame=first_frame,
            last_frame=last_frame,
            fps=fps,
            sequence_path=sequence_path,
            slate_path=slate_path,
            company=company,
            colorspace_idt=colorspace_idt,
            colorspace_odt=colorspace_odt,
        )

        # Submit to Deadline
        self.__submit_to_deadline(submission_parameters)

        return slate_path

    def __get_submission_parameters(
        self,
        plugin,
        priority,
        department,
        publish_id,
        first_frame,
        last_frame,
        fps,
        slate_path,
        sequence_path,
        company,
        colorspace_idt,
        colorspace_odt,
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
        job_info["OnJobComplete"] = "Delete"

        # Set submission name
        slate_name = os.path.basename(slate_path)
        job_info["Name"] = slate_name

        job_info["Department"] = department

        # Set slate directories for Deadline job browser
        slate_directory = os.path.dirname(slate_path)
        job_info["OutputDirectory0"] = slate_directory
        job_info["OutputFilename0"] = slate_name

        # Getting plugin submission parameters
        plugin_info = {}
        plugin_info["Version"] = 1
        plugin_info["PublishID"] = publish_id
        plugin_info["FirstFrame"] = first_frame
        plugin_info["LastFrame"] = last_frame
        plugin_info["SequencePath"] = sequence_path
        plugin_info["SlatePath"] = slate_path
        plugin_info["FPS"] = fps
        plugin_info["Company"] = company
        plugin_info["ColorspaceIDT"] = colorspace_idt
        plugin_info["ColorspaceODT"] = colorspace_odt

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
