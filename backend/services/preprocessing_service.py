import pandas as pd
import numpy as np


# Canonical feature names the model was trained on
MODEL_FEATURES = [
    'totalvisits', 'timespentonwebsite', 'pageviewspervisit',
    'asymmetricactivityscore', 'asymmetricprofilescore',
    'leadsource', 'lastactivity', 'country', 'specialization',
    'whatisyourcurrentoccupation', 'city', 'tags', 'leadquality'
]

# Fuzzy alias mapping: any column whose stripped lowercase name
# contains one of these substrings will be mapped to the canonical name.
_ALIASES = {
    'totalvisits':                ['totalvisit', 'total_visit', 'visits', 'pageview', 'visit_count'],
    'timespentonwebsite':         ['timespent', 'time_spent', 'session', 'duration'],
    'pageviewspervisit':          ['pagepervisit', 'pages_per', 'pagespervisit', 'page_per'],
    'asymmetricactivityscore':    ['activityscore', 'activity_score', 'asym_activity', 'activity'],
    'asymmetricprofilescore':     ['profilescore', 'profile_score', 'asym_profile', 'profile'],
    'leadsource':                 ['leadsource', 'lead_source', 'source', 'channel'],
    'lastactivity':               ['lastactivity', 'last_activity', 'recent_activity', 'recentact'],
    'country':                    ['country', 'nation', 'geo'],
    'specialization':             ['specialization', 'spec', 'major', 'subject', 'field'],
    'whatisyourcurrentoccupation':['occupation', 'currentoccupation', 'job', 'profession', 'employment'],
    'city':                       ['city', 'region', 'location', 'locale'],
    'tags':                       ['tag', 'segment', 'category', 'label'],
    'leadquality':                ['leadquality', 'lead_quality', 'quality', 'score', 'grade'],
}

# High-impact numeric columns that might appear in any lead file
# Used for rule-based scoring when model features are unavailable
_NUMERIC_SIGNAL_COLS = [
    'totalvisits', 'timespentonwebsite', 'pageviewspervisit',
    'asymmetricactivityscore', 'asymmetricprofilescore',
    # generic aliases
    'visits', 'timespent', 'pageviews', 'activityscore', 'profilescore',
    'score', 'engagement', 'engagement_score', 'probability', 'lead_score',
    'conversion_score', 'priority',
]


def _normalize_col(name: str) -> str:
    """Strip, lowercase, remove spaces/underscores/dashes from column name."""
    return name.lower().strip().replace(' ', '').replace('_', '').replace('-', '')


def _build_column_map(raw_columns: list) -> dict:
    """
    Returns a mapping {raw_col -> canonical_feature} for columns that
    can be confidently matched to a model feature.
    """
    norm_to_raw = {_normalize_col(c): c for c in raw_columns}
    mapping = {}
    for canonical, aliases in _ALIASES.items():
        # 1. Exact match on normalized name
        norm_canonical = _normalize_col(canonical)
        if norm_canonical in norm_to_raw:
            mapping[norm_to_raw[norm_canonical]] = canonical
            continue
        # 2. Alias substring match
        for norm_raw, raw in norm_to_raw.items():
            if raw in mapping:          # already mapped
                continue
            for alias in aliases:
                if alias in norm_raw or norm_raw in alias:
                    mapping[raw] = canonical
                    break
    return mapping


class PreprocessingService:
    def __init__(self):
        self.expected_features = MODEL_FEATURES

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flexible preprocessing that works with any CSV schema.

        Strategy:
        1. Normalize column names and attempt fuzzy matching to model features.
        2. For matched columns: fill nulls and encode categoricals with a
           consistent ordinal scheme derived from the data itself.
        3. For unmatched model features: fill with the column median (0 for
           numeric, 0 for categorical index) so the model still gets a full
           feature vector.
        4. Return a DataFrame with exactly MODEL_FEATURES columns in order.
        """
        df = df.copy()

        # --- Replace common missing-value placeholders ---
        df = df.replace(['Select', 'N/A', 'n/a', 'NA', '', '-'], np.nan)

        col_map = _build_column_map(list(df.columns))

        result = pd.DataFrame(index=df.index)

        for feature in self.expected_features:
            # Find which raw column maps to this feature (if any)
            raw_col = next((rc for rc, cf in col_map.items() if cf == feature), None)

            if raw_col is not None:
                series = df[raw_col].copy()
            else:
                # Feature not in file — fill with neutral value
                result[feature] = 0.0
                continue

            # --- Numeric features ---
            numeric_features = [
                'totalvisits', 'timespentonwebsite', 'pageviewspervisit',
                'asymmetricactivityscore', 'asymmetricprofilescore'
            ]
            if feature in numeric_features:
                series = pd.to_numeric(series, errors='coerce')
                series = series.fillna(series.median() if series.notna().any() else 0)
                result[feature] = series.astype(float)

            # --- Categorical features: ordinal encode consistently ---
            else:
                series = series.fillna('Unknown').astype(str).str.strip()
                # Build a stable sorted mapping so consistent within this call
                categories = sorted(series.unique())
                cat_map = {v: i for i, v in enumerate(categories)}
                result[feature] = series.map(cat_map).fillna(0).astype(int)

        return result

    def get_available_signal_cols(self, df: pd.DataFrame) -> list:
        """Return numeric columns that look like engagement/score signals."""
        norm_signals = {_normalize_col(c) for c in _NUMERIC_SIGNAL_COLS}
        found = []
        for c in df.columns:
            if _normalize_col(c) in norm_signals:
                found.append(c)
            elif pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() > 3:
                found.append(c)
        return found
