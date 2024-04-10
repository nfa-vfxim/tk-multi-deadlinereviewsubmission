[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/nfa-vfxim/tk-multi-deadlinereviewsubmission?include_prereleases)](https://github.com/nfa-vfxim/tk-multi-deadlinereviewsubmission) 
[![GitHub issues](https://img.shields.io/github/issues/nfa-vfxim/tk-multi-deadlinereviewsubmission)](https://github.com/nfa-vfxim/tk-multi-deadlinereviewsubmission/issues) 


# ShotGrid Deadline Review Submission <img src="icon_256.png" alt="Icon" height="24"/>

App to submit jobs to the Deadline Review Submission plugin to render mov's on the farm using Nuke.

## Requirements

| ShotGrid version | Core version | Engine version |
|------------------|--------------|----------------|
| -                | v0.14.28     | -              |

## Configuration

### Templates

| Name                 | Description                             | Default value | Fields |
|----------------------|-----------------------------------------|---------------|--------|
| `review_output_path` | Path to submit to Deadline to write to. |               |        |


### Integers

| Name               | Description                                                  | Default value |
|--------------------|--------------------------------------------------------------|---------------|
| `default_priority` | Default priority to use when submitting the job to Deadline. | 100           |


### Strings

| Name                     | Description                                                                                           | Default value            |
|--------------------------|-------------------------------------------------------------------------------------------------------|--------------------------|
| `company_name`           | The company name to add to the submission to use in the slate via the Deadline ShotGridReview plugin. | Nederlandse Filmacademie |
| `default_colorspace_idt` | Default colorspace to use as idt when submitting the job to Deadline.                                 | ACES - ACEScg            |
| `default_colorspace_odt` | Default colorspace to use as odt when submitting the job to Deadline.                                 | Output - sRGB            |


