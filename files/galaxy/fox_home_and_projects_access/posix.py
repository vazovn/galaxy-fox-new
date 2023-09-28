# Nikolay's imports
import logging
import re
from subprocess import check_output
log = logging.getLogger(__name__)
# Nikolay's imports

import functools
import os
import shutil
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from typing_extensions import Unpack

from galaxy import exceptions
from galaxy.util.path import (
    safe_contains,
    safe_path,
    safe_walk,
)
from . import (
    BaseFilesSource,
    FilesSourceOptions,
    FilesSourceProperties,
)

DEFAULT_ENFORCE_SYMLINK_SECURITY = True
DEFAULT_DELETE_ON_REALIZE = False
DEFAULT_ALLOW_SUBDIR_CREATION = True


class PosixFilesSourceProperties(FilesSourceProperties, total=False):
    root: str
    enforce_symlink_security: bool
    delete_on_realize: bool
    allow_subdir_creation: bool


class PosixFilesSource(BaseFilesSource):
    plugin_type = "posix"

    # If this were a PyFilesystem2FilesSource all that would be needed would be,
    # but we couldn't enforce security our way I suspect.
    # def _open_fs(self):
    #    from fs.osfs import OSFS
    #    handle = OSFS(**self._props)
    #    return handle

    def __init__(self, **kwd: Unpack[PosixFilesSourceProperties]):
        props = self._parse_common_config_opts(kwd)
        self.root = props.get("root")
        if not self.root:
            self.writable = False
        self.enforce_symlink_security = props.get("enforce_symlink_security", DEFAULT_ENFORCE_SYMLINK_SECURITY)
        self.delete_on_realize = props.get("delete_on_realize", DEFAULT_DELETE_ON_REALIZE)
        self.allow_subdir_creation = props.get("allow_subdir_creation", DEFAULT_ALLOW_SUBDIR_CREATION)

    ### Nikolay
    
    ### This method filters the display of the "Chose remote files". 
    ### Only the dirs owned by a group the user is member of will be shown
    
    def _get_accessible_ec_member_projects_dirs(self, full_dir_list=None, username=None):
        # get group membership of the logged user
        group_list  = check_output(['groups', username]).split()
        # filter only "ecXX-member-groups" 
        ecXX_member_groups = []
        for group in group_list:
            if re.match('^ec[0-9]+\-member\-group$', group.decode()):
                ecXX_member_groups.append(group.decode())
        filtered_dirs = []
        # filter the accessible directories
        for ec_member_group in ecXX_member_groups:
            for dir in full_dir_list :
                if ec_member_group.startswith(dir):
                   filtered_dirs.append(dir)
        return filtered_dirs


    def _list(self, path="/", recursive=True, user_context=None, opts: Optional[FilesSourceOptions] = None):
        if not self.root:
            raise exceptions.ItemAccessibilityException("Listing files at file:// URLs has been disabled.")
        dir_path = self._to_native_path(path, user_context=user_context)
        if not self._safe_directory(dir_path):
            raise exceptions.ObjectNotFound(f"The specified directory does not exist [{dir_path}].")
        if recursive:
            res: List[Dict[str, Any]] = []
            effective_root = self._effective_root(user_context)
            for p, dirs, files in safe_walk(dir_path, allowlist=self._allowlist):
                rel_dir = os.path.relpath(p, effective_root)
                to_dict = functools.partial(self._resource_info_to_dict, rel_dir, user_context=user_context)
                res.extend(map(to_dict, dirs))
                res.extend(map(to_dict, files))
            return res
        else:
            res = os.listdir(dir_path)

            ### Nikolay
            
            # 1. first condition checks if we _do actually_ list the cluster (FOX) projects dirs 
            # (effective root is defined in ../files/sources/galaxy.py in UserProjectFilesSource class
            
            # 2. second "and not" condition shall drop the filter to the content of ecXX subdirs - 
            # they shall not be filtered after the first filter has been passed : 
            # dir_path value gets extended by subdirs at every next GUI click, 
            # e.g. first pass // , second pass //ec73, thirs pass //ec73/somedir etc.
            
            if "projects" in self._effective_root(user_context) and not re.search('/ec[0-9]+$',dir_path):
                res = self._get_accessible_ec_member_projects_dirs(full_dir_list=res, username=user_context.username)

            to_dict = functools.partial(self._resource_info_to_dict, path, user_context=user_context)
            return list(map(to_dict, res))

    def _realize_to(
        self, source_path: str, native_path: str, user_context=None, opts: Optional[FilesSourceOptions] = None
    ):
        if not self.root and (not user_context or not user_context.is_admin):
            raise exceptions.ItemAccessibilityException("Writing to file:// URLs has been disabled.")

        effective_root = self._effective_root(user_context)
        source_native_path = self._to_native_path(source_path, user_context=user_context)
        if self.enforce_symlink_security:
            if not safe_contains(effective_root, source_native_path, allowlist=self._allowlist):
                raise Exception("Operation not allowed.")
        else:
            source_native_path = os.path.normpath(source_native_path)
            assert source_native_path.startswith(os.path.normpath(effective_root))

        if not self.delete_on_realize:
            shutil.copyfile(source_native_path, native_path)
        else:
            shutil.move(source_native_path, native_path)

    def _write_from(
        self, target_path: str, native_path: str, user_context=None, opts: Optional[FilesSourceOptions] = None
    ):
        effective_root = self._effective_root(user_context)
        target_native_path = self._to_native_path(target_path, user_context=user_context)
        if self.enforce_symlink_security:
            if not safe_contains(effective_root, target_native_path, allowlist=self._allowlist):
                raise Exception("Operation not allowed.")
        else:
            target_native_path = os.path.normpath(target_native_path)
            assert target_native_path.startswith(os.path.normpath(effective_root))

        target_native_path_parent = os.path.dirname(target_native_path)
        if not os.path.exists(target_native_path_parent):
            if self.allow_subdir_creation:
                os.makedirs(target_native_path_parent)
            else:
                raise Exception("Parent directory does not exist.")

        shutil.copyfile(native_path, target_native_path)

    def _to_native_path(self, source_path: str, user_context=None):
        source_path = os.path.normpath(source_path)
        if source_path.startswith("/"):
            source_path = source_path[1:]
        return os.path.join(self._effective_root(user_context), source_path)

    def _effective_root(self, user_context=None):
        return self._evaluate_prop(self.root or "/", user_context=user_context)

    def _resource_info_to_dict(self, dir: str, name: str, user_context=None):
        rel_path = os.path.normpath(os.path.join(dir, name))
        full_path = self._to_native_path(rel_path, user_context=user_context)
        uri = self.uri_from_path(rel_path)
        if os.path.isdir(full_path):
            return {"class": "Directory", "name": name, "uri": uri, "path": rel_path}
        else:
            statinfo = os.lstat(full_path)
            return {
                "class": "File",
                "name": name,
                "size": statinfo.st_size,
                "ctime": self.to_dict_time(statinfo.st_ctime),
                "uri": uri,
                "path": rel_path,
            }

    def _safe_directory(self, directory):
        if self.enforce_symlink_security:
            if not safe_path(directory, allowlist=self._allowlist):
                raise exceptions.ConfigDoesNotAllowException(
                    f"directory ({directory}) is a symlink to a location not on the allowlist"
                )

        if not os.path.exists(directory):
            return False
        return True

    def _serialization_props(self, user_context=None) -> PosixFilesSourceProperties:
        return {
            # abspath needed because will be used by external Python from
            # a job working directory
            "root": os.path.abspath(self._effective_root(user_context)),
            "enforce_symlink_security": self.enforce_symlink_security,
            "delete_on_realize": self.delete_on_realize,
            "allow_subdir_creation": self.allow_subdir_creation,
        }

    @property
    def _allowlist(self):
        return self._file_sources_config.symlink_allowlist

    def score_url_match(self, url: str):
        # For security, we need to ensure that a partial match doesn't work. e.g. file://{root}something/myfiles
        if self.root and (
            url.startswith(f"{self.get_uri_root()}://{self.root}/") or url == f"self.get_uri_root()://{self.root}"
        ):
            return len(f"self.get_uri_root()://{self.root}")
        elif self.root and (url.startswith(f"file://{self.root}/") or url == f"file://{self.root}"):
            return len(f"file://{self.root}")
        elif not self.root and url.startswith("file://"):
            return len("file://")
        else:
            return super().score_url_match(url)

    def to_relative_path(self, url: str) -> str:
        if url.startswith(f"file://{self.root}"):
            return url[len(f"file://{self.root}") :]
        elif url.startswith("file://"):
            return url[7:]
        else:
            return super().to_relative_path(url)


__all__ = ("PosixFilesSource",)