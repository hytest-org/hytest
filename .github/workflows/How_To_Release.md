# How to publish a new HyTEST release

## Essential Steps

* Make `dev` branch look like you want.
  * Merge various feature branches in to `dev` with PRs (or not... manually also works; PR preferred)
  * Direct commits to `dev` are also OK (but discouraged)
  * edit the `environment_set_up/manifest.txt` to reflect what you want in the bootstrap archive (see
    below: "What's In the Archive").
  * NOTE: you are not obligated to use `dev` -- it is just a convenient place to assemble multiple
    feature branches to ensure they work together. The rest of this workflow will still operate.
    The auto-bundling will fire with **any** merge into `main`, whether from `dev` or not.
* Create a PR to merge `dev` into `main`
  * Use github **Labels** to identify how you want the [Semantic Version](https://semver.org/) to increment:
    - No labels, increments the _patch_ number (the _p_ in 'M.m.p')<br>
      Patch updates are usually associated with minor changes meant to address problems or bugs.
    - Label "SemVer::Minor++" increments the _minor_ number (the _m_ in 'M.m.p')<br>
      A minor update includes more impactful changes, but none of them are "breaking" changes -- meaning
      that a user doesn't have to change their behavior to use the new version... changes don't break
      the user experience.
    - Label "SemVer::Major++" increments the _major_ number (the M in 'M.m.p').<br>
      Major version increments are typically associated with "breaking" changes, where the user has
      to change how they use the tool (it is 'broken' if they don't change). Example.. the change from
      Python 2.7 to 3.x includes breaking changes -- the nature of fundamental operations is different
      (e.g. the 'print' built-in works differently and is invoked differently between 2.x and 3.x)
  * These labels already exist in the repo... just apply as appropriate to reflect how
    you want the version number to increment for this new release.
* PR can be approved / reviewed / updated... with last-second changes merged into `dev`
* Merge `dev` into `main` **with a Pull Request**
  * The [github action](./release-on-pr-merge-to-main.yml) fires with this specific set of
    conditions.  A manual merge to main will not trigger.
  * Observe the run by examining the 'Actions' tab in the repo. If the action fails for some
    reason, this is where you will look for the logs and other debug information.

Upon a successful run, you should now see a new [release](https://github.com/hytest-org/hytest/releases).
Releases will be available indefinitely by referring to their GitHub **tag**, which is created
as a part of this github action.  Tags are Semantic Version numbers, preceeded with a 'v' (e.g. 'v1.2.1').
A git release is available via its version number:

```text
https://github.com/hytest-org/hytest/releases/v1.2.1
```

You can always point to the 'latest' release with the URL:

```text
https://github.com/hytest-org/hytest/releases/latest/
```

The direct link to the downloadable archive of setup materials is available with the URL:

```text
https://github.com/hytest-org/hytest/releases/latest/download/HyTEST_EnvSetUp.tar.gz
```

## What's in the Archive

The contents of the archive are intended to support the environment set up documented in our
[QuickStart for HPC](../../environment_set_up/QuickStart-HPC.md). The specific files included are
determined by the contents of the `environment_set_up/manifest.txt` file.
Put file names (one per line) in this file to see that they are included in the released archive.
The manifest file supports **simple** comments.  A `#` **as the first character** will cause
that line to be ignored.  One file per line, with a path name relative to the base of the repo.
