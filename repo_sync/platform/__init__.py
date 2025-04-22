from .github import GithubIE
from .bitbucket import BitbucketIE
from .gitee import GiteeIE
from .gitea import GiteaIE
from .gitlab import GitlabIE
from .gogs import GogsIE
from .coding import CodingIE
from .gitcode import GitcodeIE
from .aliyun import AliyunDevOpsIE

_ALL_CLASSES = [klass for name, klass in globals().items()
                if name.endswith('IE')]


def gen_extractor_classes():
    """Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_CLASSES
