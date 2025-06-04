from flask import Flask, request, jsonify, render_template
import pandas as pd
import re

app = Flask(__name__)

# Load emoji data along with sentiment scores
emoji_data = pd.read_csv('emoji_data.csv')

# Create dictionaries to map emojis to their descriptions and sentiments
emoji_to_desc = {row['emoji']: row['description'] for _, row in emoji_data.iterrows()}

def clean_sentiment(value):
    try:
        # Attempt to convert directly, assuming the value is already in a proper format.
        return float(value)
    except ValueError:
        # If there's an error, it might be due to an improperly formatted string.
        # Let's try extracting just the numeric part.
        match = re.search(r"([-+]?\d*\.\d+|\d+)", value)
        if match:
            return float(match.group(0))
        else:
            # If all else fails, return a default value such as 0.0.
            return 0.0


def get_sentiment_score(sentiment_str):
    try:
        # Convert to float if possible
        return float(sentiment_str)
    except ValueError:
        # If conversion fails, log an error and return a neutral sentiment score
        print(f"Error converting sentiment value '{sentiment_str}' to float.")
        return 0.0
    

# Then use the clean_sentiment function when loading the data
emoji_to_sentiment = {row['emoji']: clean_sentiment(row['sentiment']) for _, row in emoji_data.iterrows()}



# Load keyword sentences
keyword_sentences = pd.read_csv('food_vegetable_dessert_emotion_keyword_sentences.csv')
desc_to_emoji = {row['description']: row['emoji'] for _, row in emoji_data.iterrows()}



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    input_text = data.get('emoji', '').strip()
    response_data = []

    # Extract sentiments for each emoji in the input
    input_sentiments = [emoji_to_sentiment.get(emoji, None) for emoji in input_text if emoji in emoji_to_sentiment]

    # Handle no valid sentiments found
    if not input_sentiments:
        return jsonify({'error': 'No valid emojis or sentiments were provided.'}), 400

    # Assess overall sentiment: positive, neutral, negative
    positive_input = all(s > 0.5 for s in input_sentiments)
    negative_input = any(s < -0.5 for s in input_sentiments)
    mixed_input = not (positive_input or negative_input)
    score=0
    # Initialize a list to hold descriptions when no combinations are found
    collected_descriptions = []
    # Iterate through each emoji in the input
    for char in input_text:
        description = emoji_to_desc.get(char, '')
        if description:
            # Fetch combinations that include this description
            combinations_df = keyword_sentences[keyword_sentences['keywords'].str.contains(re.escape(description), regex=True)]
            if combinations_df.empty:
                # No combinations found, collect description
                collected_descriptions.append(description)
            else:
                for _, combo_row in combinations_df.iterrows():
                    # Split and assess sentiments of the descriptions in the combination
                    combo_descriptions = combo_row['keywords'].split('+')
                    combo_sentiments = [emoji_to_sentiment.get(desc_to_emoji.get(desc, ''), 0) for desc in combo_descriptions]

                    combo_positive = all(s > 0.5 for s in combo_sentiments)
                    combo_negative = any(s < -0.5 for s in combo_sentiments)
                    combo_mixed = any(0.6 <s < -0.4 for s in combo_sentiments)

                    # Matching based on input type
                    if (positive_input and combo_positive) or (negative_input and combo_negative) or (mixed_input and combo_negative) or(mixed_input and combo_positive ) :
                        emoji_combinations = ' '.join(desc_to_emoji.get(desc, '') for desc in combo_descriptions)
                        response_data.append({'emojis': emoji_combinations, 'sentence': combo_row['sentence'],'score':10})
                    elif (mixed_input and combo_negative) and (mixed_input and combo_positive)and(combo_mixed and combo_negative):
                        # Handle mixed sentiments by allowing any combination when input is mixed
                        emoji_combinations = ' '.join(desc_to_emoji.get(desc, '') for desc in combo_descriptions)
                        response_data.append({'emojis': emoji_combinations, 'sentence': combo_row['sentence'],'score':9})
                    elif (combo_mixed and positive_input) or (combo_mixed and negative_input):
                        emoji_combinations = ' '.join(desc_to_emoji.get(desc, '') for desc in combo_descriptions)
                        response_data.append({'emojis': emoji_combinations, 'sentence': combo_row['sentence'],'score':9.5})
                                      
        else:
            response_data.append({
                'emojis': char,
                'sentence': char,'score':0
            })
    # If no combinations for any emojis, append concatenated descriptions
    if not response_data and collected_descriptions:
        concatenated_description = ' '.join(collected_descriptions)
        response_data.append({
            'emojis': ' '.join(input_text),  # Concatenate all input emojis as a single string
            'sentence': concatenated_description,
            'score': 0
        })        
    # Sort response data by score in descending order to bring the best matches to the top
    response_data.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({'emojiCombinations': response_data})



if __name__ == '__main__':
    app.run(debug=True)