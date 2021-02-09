import os

from pathlib import Path
from typing import List, Dict

from snapfs import (
    references,
    transform,
    fs,
    head,
    stage,
    commit,
    tree,
    filters,
)
from snapfs.datatypes import (
    Branch,
    Commit,
    Difference,
    Directory,
    FileAddedDifference,
    FileUpdatedDifference,
    FileRemovedDifference,
    Head,
    Stage,
    Tag,
    Differences,
    File,
)


class DirectoryNotFoundError(FileNotFoundError):
    """
    This class represens a directory not found exception
    """


def get_repository_path(path: Path, test: bool = True) -> Path:
    repository_path = path.joinpath(".snapfs")

    if test and not repository_path.is_dir():
        raise DirectoryNotFoundError(repository_path)

    return repository_path


def get_blobs_path(path: Path, test: bool = True) -> Path:
    blobs_path = get_repository_path(path).joinpath("blobs")

    if test and not blobs_path.is_dir():
        raise DirectoryNotFoundError(blobs_path)

    return blobs_path


def get_references_path(path: Path, test: bool = True) -> Path:
    references_path = get_repository_path(path).joinpath("references")

    if test and not references_path.is_dir():
        raise DirectoryNotFoundError(references_path)

    return references_path


def get_branches_path(path: Path, test: bool = True) -> Path:
    branches_path = get_references_path(path).joinpath("branches")

    if test and not branches_path.is_dir():
        raise DirectoryNotFoundError(branches_path)

    return branches_path


def get_tags_path(path: Path, test: bool = True) -> Path:
    tags_path = get_references_path(path).joinpath("tags")

    if test and not tags_path.is_dir():
        raise DirectoryNotFoundError(tags_path)

    return tags_path


def get_stage_path(path: Path, test: bool = True) -> Path:
    stage_path = get_repository_path(path).joinpath("STAGE")

    if test and not stage_path.is_file():
        raise FileNotFoundError(stage_path)

    return stage_path


def get_head_path(path: Path, test: bool = True) -> Path:
    head_path = get_repository_path(path).joinpath("HEAD")

    if test and not head_path.is_file():
        raise FileNotFoundError(head_path)

    return head_path


def get_branches(path: Path) -> List[Branch]:
    return [
        references.load_file_as_branch(path.joinpath(x))
        for x in os.listdir(get_branches_path(path))
    ]


def get_tags(path: Path) -> List[Tag]:
    return [
        references.load_file_as_tag(path.joinpath(x))
        for x in os.listdir(get_tags_path(path))
    ]


def get_stage(path: Path) -> Stage:
    return stage.load_file_as_stage(get_stage_path(path))


def store_stage(path: Path, stage_instance: Stage) -> None:
    stage.store_stage_as_file(get_stage_path(path, False), stage_instance)


def stage_differences(
    path: Path, differences: Differences, pattern: str
) -> None:
    filtered_differences = filters.filter_differences(differences, [pattern])

    added_files = [
        x.file
        for x in filtered_differences.differences
        if isinstance(x, FileAddedDifference)
    ]

    updated_files = [
        x.file
        for x in filtered_differences.differences
        if isinstance(x, FileUpdatedDifference)
    ]

    removed_files = [
        x.file
        for x in filtered_differences.differences
        if isinstance(x, FileRemovedDifference)
    ]

    stage_instance = Stage(added_files, updated_files, removed_files)

    store_stage(path, stage_instance)


def get_head(path: Path) -> Head:
    return head.load_file_as_head(get_head_path(path))


def store_head(path: Path, head_instance: Head) -> None:
    head.store_head_as_file(get_head_path(path, False), head_instance)


def get_branch_path(path: Path, name: str, test: bool = True) -> Path:
    branch_path = get_branches_path(path).joinpath(name)

    if test and not branch_path.is_file():
        raise FileNotFoundError(branch_path)

    return branch_path


def get_branch(path: Path, name: str) -> Branch:
    return references.load_file_as_branch(get_branch_path(path, name))


def get_commit_path(path: Path, hashid: str, test: bool = True) -> Path:
    commit_path = get_blobs_path(path).joinpath(
        transform.hashid_to_path(hashid)
    )

    if test and not commit_path.is_file():
        raise FileNotFoundError(commit_path)

    return commit_path


def get_commit(path: Path, hashid: str) -> Commit:
    return commit.load_blob_as_commit(get_commit_path(path, hashid))


def branch_name_from_ref(ref: str) -> str:
    return ref.split("/").pop()


def get_commit_hashid_from_head(path: Path) -> str:
    hashid = ""

    try:
        head = get_head(path)

        if head.ref.startswith("references"):
            # reference is branch
            branch = get_branch(path, branch_name_from_ref(head.ref))

            # set hashid from branch
            hashid = branch.commit_hashid
        else:
            # reference is commit
            hashid = head.ref
    except FileNotFoundError:
        pass

    return hashid


def get_commit_from_head(path: Path) -> Commit:
    return get_commit(path, get_commit_hashid_from_head(path))


def get_tree_from_commit(path: Path, commit: Commit) -> Directory:
    return tree.load_blob_as_tree(get_blobs_path(path), commit.tree_hashid)


def checkout(path: Path, name: str) -> None:
    branch_path = get_branches_path(path).joinpath(name)
    tag_path = get_tags_path(path).joinpath(name)
    head_instace = get_head(path)

    head_data = transform.as_dict(head_instace)

    if branch_path.is_file():
        # set reference to existing branch
        reference = str(branch_path.relative_to(get_repository_path(path)))
    elif tag_path.is_file():
        # set reference to commit hashid from tag
        tag_instance = references.load_file_as_tag(tag_path)

        reference = tag_instance.commit_hashid
    else:
        # set reference to newly created branch
        commit_hashid = get_commit_hashid_from_head(path)

        branch_instance = Branch(commit_hashid)

        references.store_branch_as_file(branch_path, branch_instance)

        reference = str(branch_path.relative_to(get_repository_path(path)))

    head_data["ref"] = reference

    updated_head_instance = Head(**head_data)

    store_head(path, updated_head_instance)


def _list_to_tree(path: Path, paths: List[Path]) -> Directory:
    result = Directory()

    for item_path in paths:
        item_path_relative = item_path.relative_to(path)

        path_parts = item_path_relative.as_posix().split("/")

        if len(path_parts) > 1:
            # recursive lookup
            # add first segment as key for next directory
            first_segment = path_parts[0]

            if first_segment not in result.directories.keys():
                next_path = path.joinpath(first_segment)

                result.directories[first_segment] = _list_to_tree(
                    next_path,
                    [
                        x
                        for x in paths
                        if x.as_posix().startswith(str(next_path))
                    ],
                )
        else:
            # path_part is file
            result.files[str(item_path_relative)] = File(item_path)

    return result


def tree_from_list(path: Path, paths: List[Path]) -> Directory:
    paths_sorted = sorted(paths, key=lambda x: len(str(x).split("/")))

    return _list_to_tree(path, paths_sorted)


directory_getters = [
    get_repository_path,
    get_blobs_path,
    get_references_path,
    get_branches_path,
    get_tags_path,
]

file_getterrs = [get_stage_path, get_head_path]


def is_initialized(path: Path) -> bool:
    try:
        # access all directories
        transform.apply(lambda x: x(path), directory_getters)

        # acess all files
        transform.apply(lambda x: x(path), file_getterrs)

        return True
    except (FileNotFoundError, DirectoryNotFoundError) as e:
        print("{}: '{}'".format(e.__class__.__name__, e))

        return False


def initialize(path: Path) -> None:
    if not is_initialized(path):
        # create directories
        transform.apply(
            lambda x: fs.make_dirs(x(path, False)), directory_getters
        )

        # create new stage
        stage_instance = Stage()

        store_stage(path, stage_instance)

        # create new head
        head_instance = Head()

        store_head(path, head_instance)

        # checkout main branch
        checkout(path, "main")


def apply_additive_changes(
    path: Path, tree_list: List[File], changes: List[File]
) -> List[File]:
    result: List[File] = [*tree_list]

    existing_file_paths = [str(x.path) for x in tree_list]

    for file_instance in changes:
        file_path = str(file_instance.path)

        if file_path not in existing_file_paths:
            result.append(file_instance)
        else:
            result[existing_file_paths.index(file_path)] = file_instance

    return result


def apply_subtractive_changes(
    path: Path, tree_list: List[File], changes: List[File]
) -> List[File]:
    result: List[File] = [*tree_list]

    existing_file_paths = [str(x.path) for x in tree_list]

    for file_instance in changes:
        file_path = str(file_instance.path)

        if file_path in existing_file_paths:
            del result[existing_file_paths.index(file_path)]

    return result


if __name__ == "__main__":
    test_directory = Path(os.getcwd()).joinpath(".data/test")

    initialize(test_directory)

    # get working directory state
    # try:
    #     commit_instance = get_commit_from_head(test_directory)

    #     tree_instance = get_tree_from_commit(test_directory, commit_instance)
    # except FileNotFoundError:
    #     tree_instance = Directory()

    # working_tree_instance = tree.get_tree(test_directory)

    # differences_instance = tree.compare_trees(
    #     test_directory, working_tree_instance, tree_instance
    # )

    # transform.apply(lambda x: print(x.file), differences_instance.differences)

    # stage_differences(test_directory, differences_instance, "*")

    # commit staged files
    try:
        commit_instance = get_commit_from_head(test_directory)

        tree_instance = get_tree_from_commit(test_directory, commit_instance)
    except FileNotFoundError:
        tree_instance = Directory()

    stage_instance = get_stage(test_directory)

    tree_list = tree.tree_as_list(test_directory, tree_instance)

    updated_tree_list = apply_additive_changes(
        test_directory,
        tree_list,
        stage_instance.added_files + stage_instance.updated_files,
    )

    test_paths = [
        # File(
        #     Path(
        #         "/Users/bernhardesperester/git/python-snapfs/.data/test/setup-cinema4d/model_main_v146.c4d"
        #     )
        # )
    ]

    updated_tree_list = apply_subtractive_changes(
        test_directory, updated_tree_list, test_paths
    )

    commit_tree = tree.list_as_tree(test_directory, updated_tree_list)

    print(commit_tree.directories["setup-cinema4d"].files)

    # transform.apply(print, updated_tree_list)

    # print("before")
    # transform.apply(print, tree.tree_as_list(test_directory, tree_instance))

    # apply_added_files_changes(
    #     test_directory,
    #     tree_instance,
    #     stage_instance.added_files + stage_instance.updated_files,
    # )

    # test_paths = [
    #     Path(
    #         "/Users/bernhardesperester/git/python-snapfs/.data/test/setup-cinema4d/model_main_v146.c4d"
    #     )
    # ]

    # apply_removed_files_changes(test_directory, tree_instance, test_paths)

    # print("after")
    # transform.apply(print, tree.tree_as_list(test_directory, tree_instance))

    # added_files_tree = tree_from_list(
    #     test_directory,
    #     stage_instance.added_files
    # )

    # updated_files_tree = tree_from_list(
    #     test_directory,
    #     stage_instance.updated_files
    # )

    # removed_files_tree = tree_from_list(
    #     test_directory,
    #     stage_instance.removed_files
    # )
