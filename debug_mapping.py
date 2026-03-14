import pandas as pd
import sys
import re

# Mock ColumnMapper to see logic
class MockMapper:
    def __init__(self):
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
        self.compiled_rules = {
            model_col: [re.compile(p, re.IGNORECASE) for p in patterns]
            for model_col, patterns in self.mapping_rules.items()
        }

    def align(self, df):
        current_cols = df.columns
        new_names = {}
        matched_model_cols = set()
        
        for col in current_cols:
            found = False
            for model_col, patterns in self.compiled_rules.items():
                if model_col in matched_model_cols:
                    continue
                for pattern in patterns:
                    if pattern.search(col):
                        print(f"DEBUG: Found match! Column '{col}' -> Model Column '{model_col}' (via pattern '{pattern.pattern}')")
                        new_names[col] = model_col
                        matched_model_cols.add(model_col)
                        found = True
                        break
                if found: break
        return new_names

df = pd.read_csv(r'd:\ai-lead-conversion-system\backend\uploads\clean_combined_dataset.csv', nrows=1)
mapper = MockMapper()
mapping = mapper.align(df)
print("\nFinal Mappings:")
for k, v in mapping.items():
    print(f"  {k} -> {v}")
