#Hubsmgr - manager of remotes hubs or repositories and files

Console usage:

    usage: hubsmgr FILE_OR_DIRECTORY

Hubsmgr 

<p align="center">
    <img src="" alt="Logo" width="64" height="64">
    <h3 align="center">Hubsmgr</h3>
    <p align="center">Last version 0.1.0-a1</p>
</p>


## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
- [Usage](#usage)
- [License](#license)


## About The Project

This project is designed to make it easy to keep multiple projects in sync.

## Usage

Console usage:

    usage: hubsmgr YAML_FILE_OR_DIRECTORY

The program will load finded yaml file or all yaml files in the directory. For the processed files, folder will be created and will be synchronization by description in the contents of the yaml file.

The yaml file contains a description of the structure of projects and the order of synchronization, consisting of the following elements:
 - A named list of hubs, where each hub contains a line with the following parameters:
    - The name of the provider. Currently only git and pysync (just script sync, no support for deleting files) are supported
    - Sync options for the hub (default pull and push ):
        - pull - only download from the given pool of repositories
        - push - only upload to the given pool of repositories
        - freeze - clone only, do not update
    - managed - if the remote repository is locally available, then you can specify this option so that the script takes over the management of this remote repository and clones it if it is not there, pulling/pushing/committing if necessary on its behalf
 - Named list of categorized projects. Each project will have its own folder, categories is ignored. You can specify the following parameters as arguments to a project:
    - One or more hubs to sync with
    - Project synchronization options:
        - pull - only download this project
        - push - only upload this project
        - freeze - clone only, do not update this project
    - autocommit - if you want all changes and new files to be automatically added before synchronization
    - Other options are provider specific (see below).
 - Named list of abbreviations (shorts), where each abbreviation contains a list of arguments for projects as arguments and can be reused, including recursively

Argument lists for the elements discussed above can be specified both as yaml lists and as strings, where spaces play the role of separators.

Additional options for providers:
   - git:
      - nosubmodules - do not synchronize submodules
      - notags - do not synchronize tags
      - you can specify a list of branches to synchronize
      - you can specify a list of tags to synchronize (Free tags that point to non-commits will only be synchronized if they are specified directly)
      - you can specify specifed commit hash
      - unrelated - to allow synchronization of repositories with different histories
  - pisynk:
     - fullcmp - for full file comparison, not just modification time

Example of yaml:

    hubs:
        github: git https://github.com/username/ pull
        localhub: git ./localhub managed
    shorts:
        GitHub: github pull

    ProjectCategory:
        ProjectSubCategory:
            myproject: GitHub localhub

## License

Distributed under [the Apache 2.0 License](./LICENSE).
