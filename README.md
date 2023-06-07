# Human Compatible

[What we stand for goes here]

## Why a monorepo?

See the following for why an organisation might want to organise their code as
as monorepo:

https://monorepo.tools/

In practice, so as to be more compatible with what open source contributors
generally expect, this is a monorepo which contains within it git submodules.
This makes it not a "pure" monorepo. But, nevertheless, it should manage to
achieve the best of both worlds.

### Specifics

The goal of this public monorepository is to provide a single integration
repository. With the following benefits:

- External parties can readily reproduce the integration configuration of our
  infrastructure.
- Everyone at Human Compatible utilises a common integration code base
- GitHub integration testing can be run across inter-dependent Human Compatible
  libraries.

We make heavy use of git submodules so that smaller libraries are readily able
to be spun out into their own repo. The benefit of this is:

- We still get the above monorepo benefits
- If an external party just wants to interact with one library, they only need
  to be exposed to a smaller repository
- Easier for new-comers to understand the smaller repos

## Licensing

Everything within the public monorepo is licensed under the Apache-2.0 license.

Git submodules are licensed according to their respective repos.

## Usage of git submodules

Git submodules are used in the following ways:

- Submodules for Human Compatible developed and maintained public libraries are
  stored under `libraries/[language-name]/[submodule]`.
  - All Human Compatible repositories are found at
    `https://github.com/Human-Compatible/[submodule]` with `main` as the
    default branch.
- Submodules for third party packages are within `third-party/[submodule]`
  - All third party repositories are forked into the Human-Compatible
    organisation and a branch called `human-compatible` is created. This
    branch is then pointed to by the submodule within the monorepo.
  - The `main` / `master` branch of the forked repo is to have no extra
    commits with respect to the upstream repository.
- Any submodule which must itself be private is instead to be included within
  the `private` submodule which points to the
  `https://github.com/Human-Compatible/private` repo.

### Adding a third party submodule

After forking the third party repository into the Human-Compatible organisation
add the submodule to the monorepo. Below is an example achieving this for the
`cal.com` repository:

```bash
git submodule add -b human-compatible ../cal.com.git third-party/cal.com
```

Make sure to use a "relative URL" to the submodule, so that when someone is
cloning it they are free to use either https or ssh.
