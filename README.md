# This is the monorepo for the Human Compatible organisation

- Builds are undergone with Bazel Build
- Everything within the public monorepo is licensed under the Apache-2.0
  license
- Git submodules are licensed according to their respective repos and are
  utilised under the following scenarios:
  - Projects and files that are created by the Human Compatible organisation
    that are not able to be publicly released (all of these are found within
    the `private` submodule @ root)
  - Public third party repositories (all of these are placed within the
    `third_party` directory)
    - All third party repositories are forked into the Human-Compatible
      organisation and a branch called `human-compatible` is created. This
      branch is then pointed to by the submodule within the monorepo.
    - The `main` / `master` branch of the forked repo is to have no extra
      commits with respect to the upstream repository.
  - If you have a private `third_party` repository, or a personal repository
    that is not able to be released publicly, then please include these within
    the `private` repo, and follow the respective instructions within there.

## Adding a third party submodule

After forking the third party repository into the Human-Compatible organisation
add the submodule to the monorepo. Below is an example achieving this for the
`cal.com` repository:

```bash
git submodule add -b human-compatible git@github.com:Human-Compatible/cal.com.git third_party/cal.com
```
