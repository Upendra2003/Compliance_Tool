from . import a_notice
from . import b_consent
from . import c_retention
from . import d_deletion
from . import e_data_minimization

ALL_CHECK_GROUPS={
    "notice": a_notice,
    "consent": b_consent,
    "retention": c_retention,
    "deletion": d_deletion,
    "data_minimization": e_data_minimization
}