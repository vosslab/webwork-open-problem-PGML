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
_DBCHAPTER_LINE_RX = re.compile(r"(?m)^[ \t]*##[ \t]*DBchapter\(([^)]*)\)")
_DBSECTION_LINE_RX = re.compile(r"(?m)^[ \t]*##[ \t]*DBsection\(([^)]*)\)")

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


def extract_dbsubjects_pairs(text: str) -> list[tuple[str, str]]:
	"""
	Return DBsubject entries as (raw, normalized) pairs.

	Only lines matching the pattern are counted:
	  ^##\\s*DBsubject\\(

	raw:
	- first argument only (split on the first comma)
	- strip surrounding quotes (single or double)
	- trim leading/trailing whitespace
	- preserve case and internal whitespace

	normalized:
	- lowercased
	- internal whitespace collapsed
	- minimal typo fixups applied
	"""
	return _extract_dbtag_pairs(text, rx=_DBSUBJECT_LINE_RX, normalize=_normalize_subject_value)


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
	return [norm for _raw, norm in extract_dbsubjects_pairs(text)]


def extract_dbchapters_pairs(text: str) -> list[tuple[str, str]]:
	"""
	Return DBchapter entries as (raw, normalized) pairs.
	"""
	return _extract_dbtag_pairs(text, rx=_DBCHAPTER_LINE_RX, normalize=_normalize_dbtag_value)


def extract_dbsections_pairs(text: str) -> list[tuple[str, str]]:
	"""
	Return DBsection entries as (raw, normalized) pairs.
	"""
	return _extract_dbtag_pairs(text, rx=_DBSECTION_LINE_RX, normalize=_normalize_dbtag_value)


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
	raw = _raw_dbtag_arg(arg_text)
	return _normalize_subject_value(raw)


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


def _normalize_dbtag_value(value: str) -> str:
	s = value.strip().lower()
	s = " ".join(s.split())
	return s


def _contains_any(text: str, substrings: tuple[str, ...]) -> bool:
	for sub in substrings:
		if sub in text:
			return True
	return False


def _raw_dbtag_arg(arg_text: str) -> str:
	"""
	Return a raw tag argument with quotes stripped and whitespace trimmed.
	"""
	s = arg_text.strip()
	if not s:
		return ""

	if s[0] in ("'", '"'):
		quote = s[0]
		out: list[str] = []
		escape = False
		for ch in s[1:]:
			if escape:
				out.append(ch)
				escape = False
				continue
			if ch == "\\":
				escape = True
				continue
			if ch == quote:
				break
			out.append(ch)
		return "".join(out).strip()

	# Unquoted: treat a comma as separating additional args.
	if "," in s:
		s = s.split(",", 1)[0].strip()
	return s


def _extract_dbtag_pairs(text: str, *, rx: re.Pattern, normalize) -> list[tuple[str, str]]:
	pairs: list[tuple[str, str]] = []
	for m in rx.finditer(text):
		arg_text = m.group(1)
		raw = _raw_dbtag_arg(arg_text)
		norm = normalize(raw)
		pairs.append((raw, norm))
	return pairs


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


def chem_terms_present(text: str) -> list[str]:
	"""
	Return unique chemistry hint terms present in the file (case-insensitive).
	"""
	if not isinstance(text, str) or not text:
		return []
	low = text.lower()
	return [t for t in _CHEM_HINT_TERMS if t in low]


def bio_terms_present(text: str) -> list[str]:
	"""
	Return unique biology hint terms present in the file (case-insensitive).
	"""
	if not isinstance(text, str) or not text:
		return []
	low = text.lower()
	return [t for t in _BIO_HINT_TERMS if t in low]
