import pandas as pd
import re

class ColumnMapper:
    def __init__(self):
        # Default mappings for common lead dataset columns
        self.mapping_rules = {
            'leadsource': [r'source', r'lead_source', r'origin'],
            'totalvisits': [r'visits', r'total_visits', r'web_visits'],
            'timespentonwebsite': [r'time', r'time_spent', r'duration', r'total_time_spent_on_website'],
            'pageviewspervisit': [r'page_views', r'views_per_visit', r'page_views_per_visit'],
            'lastactivity': [r'activity', r'last_activity'],
            'country': [r'country', r'location'],
            'specialization': [r'specialization', r'interest'],
            'howdidyouhearaboutus': [r'how_did_you_hear', r'referral', r'how_did_you_hear_about_x_education'],
            'whatisyourcurrentoccupation': [r'occupation', r'job_role', r'what_is_your_current_occupation'],
            'whatisyourmainsettlementreason': [r'reason', r'settlement'],
            'newspaperarticle': [r'newspaper_article'],
            'xeducationforums': [r'forums', r'x_education_forums'],
            'newspaper': [r'news', r'newspaper'],
            'digitaladvertisement': [r'ad', r'digital_ad'],
            'throughrecommendations': [r'recommendation'],
            'receivemoreupdatesaboutourcourses': [r'updates', r'receive_more_updates_about_our_courses'],
            'tags': [r'tags'],
            'leadquality': [r'quality', r'lead_quality'],
            'updatemeonsupplychaincontent': [r'supply_chain', r'update_me_on_supply_chain_content'],
            'getupdatesondmcontent': [r'dm_content', r'get_updates_on_dm_content'],
            'leadprofile': [r'profile', r'lead_profile'],
            'city': [r'city'],
            'asymmetricactivityindex': [r'activity_index', r'asymmetrique_activity_index'],
            'asymmetricactivityscore': [r'activity_score', r'asymmetrique_activity_score'],
            'asymmetricprofileindex': [r'profile_index', r'asymmetrique_profile_index'],
            'asymmetricprofilescore': [r'profile_score', r'asymmetrique_profile_score'],
            'iagreetopaytheamountthroughcheque': [r'cheque', r'i_agree_to_pay_the_amount_through_cheque'],
            'freecopyofmasteringpython': [r'free_copy', r'python_book', r'a_free_copy_of_mastering_the_interview'],
            'lastnotableactivity': [r'notable_activity', r'last_notable_activity']
        }
        self.required_columns = list(self.mapping_rules.keys())
        # Pre-compile patterns for performance
        self.compiled_rules = {
            model_col: [re.compile(p, re.IGNORECASE) for p in patterns]
            for model_col, patterns in self.mapping_rules.items()
        }

    def align_columns(self, df):
        """
        Rename columns based on rules and return a dataframe with strictly required columns.
        """
        current_cols = df.columns
        new_names = {}
        matched_model_cols = set()
        
        # 1. First Pass: Check if any columns ALREADY match model feature names
        # We process these first to prevent renames from colliding with them
        for col in current_cols:
            col_lower = col.strip().lower()
            if col_lower in self.mapping_rules:
                new_names[col] = col_lower
                matched_model_cols.add(col_lower)
        
        # 2. Second Pass: Use regex patterns for unmapped columns
        for col in current_cols:
            if col in new_names:
                continue
                
            found = False
            for model_col, patterns in self.compiled_rules.items():
                if model_col in matched_model_cols:
                    continue
                for pattern in patterns:
                    if pattern.search(col):
                        new_names[col] = model_col
                        matched_model_cols.add(model_col)
                        found = True
                        break
                if found: break
        
        df = df.rename(columns=new_names)
        
        # Ensure unique columns by dropping duplicates (favoring the one we mapped correctly)
        # If collisions still exist (unlikely with this logic), keep first
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        # Vectorized addition of missing columns
        missing_cols = list(set(self.required_columns) - set(df.columns))
        if missing_cols:
            # Create a small DF of NaNs and join for efficiency
            missing_df = pd.DataFrame(index=df.index, columns=missing_cols)
            df = pd.concat([df, missing_df], axis=1)
        
        return df[self.required_columns]
