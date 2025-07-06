# Multimodal Zero-Shot Prompting With Gemini 2.5 Flash
<a href="https://colab.research.google.com/drive/1tXMiyrs-MOJK7rDeAiLNJbja_fVApU32?usp=sharing" target="_blank">
  <img src="https://colab.research.google.com/img/colab_favicon_256px.png" alt="Open Colab Notebook" width="28" style="vertical-align: middle; margin-right: 8px;">
  <span style="font-size: 16px; vertical-align: middle;">Open Colab Notebook</span>
</a>



## Introduction

The topic of context engineering is on the rise, as professionals in the AI industry indicate that simply instructing large models to do particular tasks is not enough to build robust and scalable solutions. Instead, you have to carefully curate your media and feed it to the model or agentic system at appropriate time in appropriate form. We are witnessing the dawn of content management systems for LLM/VLM orchestration purposes.

In the current article, we are going to demonstrate one of the approaches to effective usage of video data for the in-context learning with Gemini 2.5 Flash. We are absolutely aware that the topic of multimodal prompting is not new, but our goal here is to show how to organize such pipeline in practice so it can be further scaled for real-world applications.

We are going to solve the task of action summarization on the video (Parallel Parking) to provide the user with suggestions which driving maneuvers could have been done better. We are viewing the parking as a sort of non-trivial process in this case, assuming that generic VLM like Gemini might not have enough knowledge to provide a valuable response.

## Data

Let's start by viewing the video we would like to analyze (click the image to watch the video on YouTube):

[![Watch on YouTube](https://img.youtube.com/vi/rbG0chQQnBA/0.jpg)](https://www.youtube.com/watch?v=rbG0chQQnBA)



As you can see, the parking attempt is not going perfectly, and the driver makes corrections. We are however interested in what exactly was done non-efficient and how to improve it.

## Prompting

Let's proceed with setting up a client and building a prompt. While Google GenAI SDK is changing dynamically, the current tutorial assumes version `1.20.0` of the SDK.

```bash
pip install google-genai==1.20.0
```

```python
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
```

The text prompts are trivial:

```python
system_prompt = "You are a helpful driving assistant who provide concise and focused answer to guarantee driver's safety"
task_prompt = (
    "Is the drive making correct movements during parking? Analyze the movements made by the driver and"
    "recommend corrections wherever necessary. Be concise"
)
```

We are now going to use SDK to build a full Context Prompt with both text and video data. The video was previously uploaded to the Gemini endpoint via the File API. View full example in Colab for more details.

```python
from google.genai.types import Content, Part
```

```python
content = Content(
    role="user",
    parts=[
        Part(text=task_prompt),
        Part.from_uri(
            file_uri=input_uri.uri, mime_type='video/mp4')
    ]
)
```

And now let's finally call our client to get the response:

```python
from google.genai.types import GenerateContentConfig

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[content],
    config=GenerateContentConfig(
        temperature=0.0,
        system_instruction=system_prompt

    )
)
```

We are getting something like this:

```
The driver's movements were generally correct for parallel parking, but lacked precision.

**Recommendations:**
1.  **Initial Angle:** Turn the steering wheel more sharply to the right when first reversing to achieve a better angle into the spot.
2.  **Depth:** Reverse further back before straightening the wheels to ensure the front of the car clears the vehicle ahead and can be brought closer to the curb.
3.  **Final Adjustment:** Make smaller, more controlled adjustments to achieve a perfectly parallel position closer to the curb.
```

So far so good. As we can see from response, Gemini succesfully recognizes that parking attempt was problematic and suggested some corrective actions. Let's  see how we can further improve the level of detail and quality of corrections by leveraging zero-shot prompting.

## Zero-Shot Prompting

Let's start with viewing our instruction video:

[![Watch on YouTube](https://img.youtube.com/vi/Q-cfrY45Yaw/0.jpg)](https://www.youtube.com/watch?v=Q-cfrY45Yaw)

The instruction video also has a soundtrack which will be additionally utilized by Gemini to retrieve even more contextual information.

Let's proceed with creating instructions for the in-context learnining and collect a new `Content` object:

```python
learning_prompt = (
    "Learn from the instructions provided in the following video and thoroughly apply them to further input to search for"
    "errors and to make suggestions. Analyze video step by step"
)
```
```python
zeroshot_content = Content(
    role="user",
    parts=[
        Part(text=learning_prompt),
        Part.from_uri(
            file_uri=instruction_uri, mime_type='video/mp4')
    ]
)
```

Finally, let's prepend the new **learning** content to the original prompt and call the client again:

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[zeroshot_content, content],
    config=GenerateContentConfig(
        temperature=0.0,
        system_instruction=system_prompt

    )
)
```

We are getting the response like this:

```
Based on the video instructions, here are the errors and suggestions for the driver's parallel parking attempt:

**Errors:**

1.  **Initial Distance:** The driver was too far from the white SUV. The video suggests 2-3 feet.
2.  **Initial Alignment:** The driver aligned their rear bumper with the white SUV's rear bumper. For a larger vehicle, the video instructs aligning your **brake lights** with the parked car's brake lights. This incorrect starting point led to being too far from the curb.
3.  **Angle of Reversal:** The initial 45-degree angle was likely too shallow or not maintained correctly, causing the car to swing out too wide.

**Suggestions:**

1.  **Reduce Initial Gap:** Position your car closer to the parked vehicle, aiming for about 2-3 feet of space.
2.  **Correct Alignment:** When parking behind a larger vehicle, pull forward until your **rear brake lights** are aligned with the rear brake lights of the car you're parking behind.
3.  **Utilize Mirror Cues:** Pay close attention to the mirror cues from the video:
    *   In your left mirror, look for the headlights of the car behind you.
    *   In your right mirror, ensure it covers the left brake lights of the car next to you.
    *   These cues indicate when to turn your wheel fully to the left.
```

As you can see, the response is much more detailed and contains a lot of useful information, that can be further granularized into Action Items and be communicated to the driver.

## Conclusions

This was a fast demostration of current prompting capabilities of large VLMs like Gemini. The ability to seamlessly combine different types of content in the prompts open powerful possibilities such as:

* Media context pipelines for model instructions and retrieval in RAG/KAG;
* Advanced agentic capabilities with reasoning based on multimodal input analysis
* Connections with other Computer Vision models for covering topics that VLMs don't have access to (e.g. 3D mutual car orientation)


## References

* [Gemini 2.5 Flash](https://huggingface.co/google/gemini-2.5-flash)
* [Google GenAI](https://developers.generativeai.google/guide/overview)