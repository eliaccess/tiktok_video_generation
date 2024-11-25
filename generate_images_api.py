import replicate
import dotenv

dotenv.load_dotenv()

prompt = """
"scene_description": "The ghost reaches out towards Lily, her hand trembling slightly as if pleading for assistance. The air feels thick with desperation and longing, creating a powerful emotional impact.",
"lighting": "The stark contrast between the shadowy room and the illuminated figure exaggerates the ghost's plea.",
"details": "The sound of the whispering winds outside seems to swell, complementing the ghost's haunting words."
"security": no nudity, no extremely gore content, no violence, no hate speech, no racism, no sexism, no copyrighted material"""

def generate_image(prompt, output_name):
    input = {
        "output_format": "jpg",
        "aspect_ratio": "9:16",
        "go_fast": False,
        "megapixels": "1",
        "output_quality": 100,
        "prompt": prompt
    }

    model = "black-forest-labs/flux-dev" # "black-forest-labs/flux-pro"

    output = replicate.run(
        model,
        input=input
    )

    print(output)
    with open(f"{output_name}.png", "wb") as file:
        file.write(output[0].read())

if __name__ == "__main__":
    generate_image(prompt, "output_name.png")