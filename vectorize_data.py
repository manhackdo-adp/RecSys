import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class Vectorizer:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        
    def process_dataframe(self, df):
        if '내용2' in df.columns:
            df['내용'] = df['내용1'] + df['내용2']
            df.drop(columns=['내용1', '내용2'], inplace=True)
        elif '내용1' in df.columns:
            df.rename(columns={'내용1': '내용'}, inplace=True)
        
    def make_vectors(self, df):
        self.process_dataframe(df)
        vector_list = []
        for index, row in tqdm(df.iterrows(), total=len(df)):
            sentences = str(row['내용']) if not pd.isnull(row['내용']) else ''
            vectors = self.model.encode(sentences)
            vector_list.append(vectors)
        df['vectors'] = vector_list

def clean_df(df):
    df.dropna(subset=['내용'], inplace=True)
    return df

if __name__ == "__main__":
    exhibit_df = pd.read_csv("exhibit_df.csv")
    festival_df = pd.read_csv("festival_data.csv")
    musical_df = pd.read_csv("musical_all_df.csv")

    vectorizer = Vectorizer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    vectorizer.make_vectors(exhibit_df)
    vectorizer.make_vectors(festival_df)
    vectorizer.make_vectors(musical_df)

    exhibit_df = clean_df(exhibit_df)
    festival_df = clean_df(festival_df)
    musical_df = clean_df(musical_df)

    exhibit_df.to_csv("clean_exhibit_df.csv", index=False)
    festival_df.to_csv("clean_festival_df.csv", index=False)
    musical_df.to_csv("clean_musical_df.csv", index=False)
