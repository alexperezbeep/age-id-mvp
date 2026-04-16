🛠️ AGE Context-Lock Identifier
Standardized Visual-First Profiling for the 92nd MXS

Step 1: Select Equipment Category
Identify Category:

Heater / Environmental Control
Step 2: Describe Physical Profile
What does it look like?


[Not Sure]


Modern (Yellow / Enclosed)


Legacy (Grey / Exposed Frame)


Small (Portable Square)

Step 3: Scan & Identify
Upload unit photo...

No file chosen
Screens....52 AM.png
2.7MB
0
Unit Scan


google.genai.errors.ClientError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/age-id-mvp/app.py", line 87, in <module>
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Latest model for fast extraction
    ...<3 lines>...
        )
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/models.py", line 6276, in generate_content
    response = self._generate_content(
        model=model, contents=contents, config=parsed_config
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/models.py", line 4730, in _generate_content
    response = self._api_client.request(
        'post', path, request_dict, http_options
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/_api_client.py", line 1537, in request
    response = self._request(http_request, http_options, stream=False)
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/_api_client.py", line 1332, in _request
    return self._retry(self._request_once, http_request, stream)  # type: ignore[no-any-return]
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/tenacity/__init__.py", line 470, in __call__
    do = self.iter(retry_state=retry_state)
File "/home/adminuser/venv/lib/python3.14/site-packages/tenacity/__init__.py", line 371, in iter
    result = action(retry_state)
File "/home/adminuser/venv/lib/python3.14/site-packages/tenacity/__init__.py", line 413, in exc_check
    raise retry_exc.reraise()
          ~~~~~~~~~~~~~~~~~^^
File "/home/adminuser/venv/lib/python3.14/site-packages/tenacity/__init__.py", line 184, in reraise
    raise self.last_attempt.result()
          ~~~~~~~~~~~~~~~~~~~~~~~~^^
File "/usr/local/lib/python3.14/concurrent/futures/_base.py", line 443, in result
    return self.__get_result()
           ~~~~~~~~~~~~~~~~~^^
File "/usr/local/lib/python3.14/concurrent/futures/_base.py", line 395, in __get_result
    raise self._exception
File "/home/adminuser/venv/lib/python3.14/site-packages/tenacity/__init__.py", line 473, in __call__
    result = fn(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/_api_client.py", line 1309, in _request_once
    errors.APIError.raise_for_response(response)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/errors.py", line 155, in raise_for_response
    cls.raise_error(response.status_code, response_json, response)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/genai/errors.py", line 184, in raise_error
    raise ClientError(status_code, response_json, response)
