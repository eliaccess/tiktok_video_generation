from openai import OpenAI
import dotenv

api_key_openai = dotenv.get_key(dotenv_path=".env", key_to_get="OPENAI_API_KEY")

client = OpenAI(api_key=api_key_openai)
model = "gpt-4o-mini"
prompt_story_generation = """Write a captivating story based on a theme provided by the user. The story should follow a narrative arc, including an engaging introduction, a well-developed plot with rising tension, and a satisfying resolution or cliffhanger. The tone, setting, and characters should align with the chosen theme. Use vivid descriptions, emotional depth, and immersive details to bring the story to life. Include moments of suspense, surprise, or introspection to maintain the reader’s interest.
For example, if the user specifies a theme like horror, create a setting that evokes dread and unease, with atmospheric elements like eerie locations, unsettling objects, or unexplained phenomena. Develop a protagonist with relatable emotions and reactions to the unfolding events. Conclude with a twist, unresolved mystery, or chilling realization to leave a lasting impression.
The story should be approximately 500 words but can adapt based on the user's preference.
Export to json, with no Markdown formatting, respecting the format:
{
  "story": "Once upon a time...",
  "theme": "horror",
  "title": "The Haunted House"
}"""

prompt_story_split_description = """Given a story written by the user, break it into small, coherent chunks and represent each chunk in JSON format. Each chunk should correspond to a segment of the story that can be visualized as a single image, with detailed descriptions to guide an image generation system. The JSON format should follow this structure:  
[
  {
    "id": <unique ID for the chunk, starting from 0>,
    "text": "<short portion of the story>",
    "scene_description": "<detailed description of the scene corresponding to the text, with a focus on imagery and atmosphere>",
    "lighting": "<lighting description for the scene>",
    "details": "<specific objects, sounds, or actions that add depth to the scene>"
  },
  ...
]

Requirements:  
1. Chunk Size: Keep each chunk's text concise, focusing on a single scene or action that can be captured in one image.  
2. Scene Description: Provide a detailed and vivid description of the corresponding scene, emphasizing atmosphere, spatial arrangement, and key visual elements.  
3. Lighting and Details: Use the 'lighting' and 'details' fields to enhance the scene's mood and immersion.  
4. Theme Alignment: Ensure that the scene descriptions match the tone and theme of the story (e.g., suspenseful and eerie for horror, whimsical for fantasy).  

Example:  
If the story is:  
"It started as a simple weekend trip to visit my grandparents' old house before it was sold. I hadn't been there in years, not since my childhood summers spent roaming the woods and dusty halls. The house, long forgotten by everyone except my father's lawyer, loomed on the edge of a forgotten town, surrounded by towering pines that creaked with each whisper of wind."

The JSON output would be:  
[
  {
    "id": 0,
    "text": "It started as a simple weekend trip to visit my grandparents' old house before it was sold. I hadn't been there in years, not since my childhood summers spent roaming the woods and dusty halls.",
    "scene_description": "A dusk-lit scene of an old, imposing house surrounded by tall, swaying pine trees. The house appears slightly dilapidated, with cracked windows and ivy climbing its walls. The environment is quiet and eerie, with faint fog at the ground level, adding to the foreboding atmosphere. The trees creak subtly as if whispering secrets.",
    "lighting": "Dim and moody, with warm tones transitioning to deep blue shadows.",
    "details": "Wind rustles the tree branches, casting moving shadows on the house's façade."
  },
  {
    "id": 1,
    "text": "The house, long forgotten by everyone except my father's lawyer, loomed on the edge of a forgotten town, surrounded by towering pines that creaked with each whisper of wind.",
    "scene_description": "A view of the old house at twilight, perched on the edge of an overgrown town. The pines tower ominously around it, their dark silhouettes swaying slightly against a dusky sky.",
    "lighting": "The soft glow of twilight fades into deep blue shadows cast by the trees.",
    "details": "The pines' branches creak and sway faintly, creating a whispering sound that heightens the sense of isolation."
  }
]

Use this format to structure the entire story in a way that each scene is visually and descriptively clear. Do not use any Markdown formatting."""

def call_openai_chat(model, messages):
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content

def generate_story(theme):
    messages = [
        {"role": "system", "content": prompt_story_generation},
        {"role": "user", "content": theme}
    ]
    return call_openai_chat(model, messages)

def extract_story(response):
    import json
    data = json.loads(response)
    return data

def export_story(content):
    import json
    with open("data/story.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(content, ensure_ascii=False, indent=4))
        
def split_story_paragraphs(story):
    paragraphs = []
    messages = [
        {"role": "system", "content": prompt_story_split_description},
        {"role": "user", "content": story}
    ]
    paragraphs = call_openai_chat(model, messages)
    paragraphs = extract_story(paragraphs)
    return paragraphs

if __name__ == "__main__":
    theme = "horror, ghost, vacation"
    story = generate_story(theme)
    story_json = extract_story(story)
    story_json["story"] = split_story_paragraphs(story_json["story"])
    export_story(story_json)
    print(story)