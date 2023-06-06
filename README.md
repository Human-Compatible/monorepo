# This is the monorepo for the Human Compatible organisation

- Builds are undergone with Bazel Build
- Everything within the public monorepo is licensed under the Apache-2.0
  license
- Git submodules are licensed according to their respective repos and are
  utilised under the following scenarios:
  - Projects and files that are created by the Human Compatible organisation
    that are not able to be publicly released (all of these are found within
    the `private` submodule @ root)
  - Third party repositories (all of these are placed within the `third_party`
    directory)
