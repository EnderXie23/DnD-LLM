# NLP-Project

Now we have a smarter implementation of parser. It can parse the following grammar:

```
Title 1
content 1 for all players.
content 1 only for DM.

Title 2
content 2 for all players.
content 2 only for DM.
```
into the following structure:

```
[
    {
        "name": "Title 1",
        "public": "content 1 for all players.",
        "private": "content 1 only for DM."
    },
    {
        "name": "Title 2",
        "public": "content 2 for all players.",
        "private": "content 2 only for DM."
    }
]
```

The contents for all players and DM are judged by the LLM agent itself. If there is no content for public / DM, the corresponding field will be empty.

Note: to run this parser, you need to create a `.dotenv` file in the root directory with the following content:

```
DEEPSEEK_API_KEY=your_api_key
```

You can also use other APIs to judge the content, but you need to modify the code in `parser.py`.
