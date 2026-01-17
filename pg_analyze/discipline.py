"""
Discipline breakdown via DBsubject metadata.

This module is intentionally lightweight: it scans for DBsubject(...) lines and
applies substring-based bucketing.
"""

# Standard Library
import re


#============================================


DISCIPLINES = (
	"chemistry",
	"life_sciences",
	"engineering",
	"physics",
	"stats",
	"math",
	"cs",
	"finance",
	"grade_level",
	"meta_noise",
	"meta_missing",
	"other",
)

_DBSUBJECT_LINE_RX = re.compile(r"(?m)^[ \t]*##[ \t]*DBsubject\(([^)]*)\)")

_CHEM_HINT_TERMS = (
	"chemistry",
	"organic",
	"inorganic",
	"biochemistry",
	"spectroscopy",
	"kinetics",
	"equilibrium",
)

_BIO_HINT_TERMS = (
	"biology",
	"anatomy",
	"physiology",
)

_CHEMISTRY_SUBSTRINGS = (
	"chem",
	"chemistry",
	"organic",
	"inorganic",
	"biochem",
	"biochemistry",
	"analytical",
	"physical chemistry",
	"pchem",
	"spectroscopy",
	"kinetics",
	"equilibrium",
)

_LIFE_SCIENCES_SUBSTRINGS = (
	"biology",
	"biological",
	"anatomy",
	"physiology",
	"life science",
	"life sciences",
)

_ENGINEERING_SUBSTRINGS = (
	"engineering",
	"electrical engineering",
	"mechanical engineering",
	"materials engineering",
	"material science",
	"materials science",
	"circuits",
	"electric circuits",
	"controls",
	"control",
	"signals and systems",
	"signals",
	"signal",
	"systems",
	"system",
	"statics",
	"dynamics",
	"mechanics of materials",
	"strength of materials",
	"fluid",
	"fluids",
	"fluid mechanics",
	"thermodynamics",
	"heat transfer",
	"numerical methods",
	"finite element",
	"fea",
)

_PHYSICS_SUBSTRINGS = (
	"physics",
	"modern physics",
	"mechanics",
	"optics",
	"electricity",
	"quantum",
	"nuclear",
	"particle",
	"atomic",
	"waves",
	"gravitation",
)

_STATS_SUBSTRINGS = (
	"stat",
	"probab",
	"stochastic",
	"bayes",
	"regression",
	"inference",
)

_MATH_SUBSTRINGS = (
	"arithmetic",
	"integers",
	"numbers",
	"lines and linear functions",
	"linear functions",
	"algebra",
	"calculus",
	"trigon",
	"geometry",
	"number theory",
	"linear algebra",
	"differential equations",
	"analysis",
	"discrete",
	"combinatorics",
	"set theory",
	"logic",
)

_CS_SUBSTRINGS = (
	"computer science",
	"programming",
	"algorithm",
	"algorithms",
	"data structure",
	"data structures",
)

_FINANCE_SUBSTRINGS = (
	"financial",
	"finance",
	"econom",
	"accounting",
)

_META_SUBSTRINGS = (
	"webwork",
	"zzz-inserted text",
	"history",
	"necap",
)

_GRADE_LEVEL_SUBSTRINGS = (
	"middle school",
	"elementary school",
)

_MISSING_SUBSTRINGS = (
	"tba",
	"subject",
	"course",
)

_TYPO_FIXUPS = {
	"thermodyanmics": "thermodynamics",
	"thermodyanamics": "thermodynamics",
	"mechanica": "mechanical",
}


#============================================


def extract_dbsubjects(text: str) -> list[str]:
	"""
	Return DBsubject entries found in a PG file.

	Only lines matching the pattern are counted:
	  ^##\\s*DBsubject\\(

	The extracted subject string is normalized by:
	- taking only the first argument (split on the first comma)
	- stripping surrounding quotes (single or double)
	- trimming whitespace
	- lowercasing
	"""
	subjects: list[str] = []
	for m in _DBSUBJECT_LINE_RX.finditer(text):
		arg_text = m.group(1)
		subjects.append(_normalize_subject_arg(arg_text))
	return subjects


def bucket_subject(subject: str) -> str:
	"""
	Bucket a normalized subject into a coarse discipline.
	"""
	s = _normalize_subject_value(subject)
	if not s:
		return "meta_missing"

	if s in _MISSING_SUBSTRINGS:
		return "meta_missing"

	if _contains_any(s, _GRADE_LEVEL_SUBSTRINGS):
		return "grade_level"

	if _contains_any(s, _META_SUBSTRINGS):
		return "meta_noise"

	if _contains_any(s, _CHEMISTRY_SUBSTRINGS):
		return "chemistry"
	if _contains_any(s, _LIFE_SCIENCES_SUBSTRINGS):
		return "life_sciences"
	if _contains_any(s, _ENGINEERING_SUBSTRINGS):
		return "engineering"
	if _contains_any(s, _PHYSICS_SUBSTRINGS):
		return "physics"
	if _contains_any(s, _STATS_SUBSTRINGS):
		return "stats"
	if _contains_any(s, _MATH_SUBSTRINGS):
		return "math"
	if _contains_any(s, _CS_SUBSTRINGS):
		return "cs"
	if _contains_any(s, _FINANCE_SUBSTRINGS):
		return "finance"
	return "other"


def analyze_text(text: str) -> dict:
	subjects = extract_dbsubjects(text)
	disciplines = [bucket_subject(s) for s in subjects]
	primary = primary_discipline(subjects)
	return {
		"subjects": subjects,
		"disciplines": disciplines,
		"primary": primary,
	}


def analyze_file(path: str) -> dict:
	with open(path, "r", encoding="latin-1") as f:
		return analyze_text(f.read())


def primary_discipline(subjects: list[str]) -> str:
	"""
	Return the per-file discipline based on the first non-blank DBsubject line.

	If no DBsubject lines exist (or all are blank), returns "other".
	"""
	for s in subjects:
		if isinstance(s, str) and s.strip():
			return bucket_subject(s)
	return "other"


#============================================


def _normalize_subject_arg(arg_text: str) -> str:
	s = arg_text.strip()
	if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
		s = s[1:-1].strip()
	return _normalize_subject_value(s)


def primary_subject(subjects: list[str]) -> str:
	for s in subjects:
		if isinstance(s, str) and s.strip():
			return _normalize_subject_value(s)
	return ""


def _normalize_subject_value(value: str) -> str:
	s = value.strip().lower()
	for bad, good in _TYPO_FIXUPS.items():
		if bad in s:
			s = s.replace(bad, good)
	s = " ".join(s.split())
	return s


def _contains_any(text: str, substrings: tuple[str, ...]) -> bool:
	for sub in substrings:
		if sub in text:
			return True
	return False


def first_content_hint(text: str, *, terms: tuple[str, ...]) -> tuple[str, int, str] | None:
	"""
	Return the first (term, line_number, line_text) match for the given terms.

	This is an audit-only helper; it is not used for discipline classification.
	"""
	if not isinstance(text, str) or not text:
		return None
	low = text.lower()
	for term in terms:
		if term not in low:
			continue
		for i, line in enumerate(text.splitlines(), start=1):
			if term in line.lower():
				return term, i, line.strip()
	return None


def first_chem_hint(text: str) -> tuple[str, int, str] | None:
	return first_content_hint(text, terms=_CHEM_HINT_TERMS)


def first_bio_hint(text: str) -> tuple[str, int, str] | None:
	return first_content_hint(text, terms=_BIO_HINT_TERMS)
