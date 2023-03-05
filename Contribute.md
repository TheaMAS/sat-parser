To contribute to this repository, please consider the following best practices:

1. Create a branch off master. Name the branch something relevant to the feature you are working on:

```
git checkout master
git checkout -b feature_to_be_added
```

2. While working on your code, please use commit messages to describe work accomplished within the commit. Continue to push to your branch.

3. When your branch is pushed and ready, merge it with dev:

```
git checkout dev
git pull origin feature_to_be_added
git push origin dev
```

4. In the dev branch, see if your code changes work. If so, merge your branch with master and push the code. You should be asked to create a pull request. Do so now.

```
git checkout master
git pull origin feature_to_be_added
git push origin master
```

We will then review the code.
