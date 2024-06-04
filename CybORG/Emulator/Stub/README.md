# manage_yaml.py and interact_yaml.py

``manage_yaml.py`` and ``interact_yaml.py`` are a server and client, respectfully, for managing YAML file,
specifically for querying and modifying YAML files.  They use the client/server model of ZeroMQ.

The reason for using client/server to manage YAML files, is to allow multiple processes to access the same YAML file.
By doing this through client/server, the requests are executed in a first-come-first-served order.

## How to use the manage_yaml.py

``manage_yaml.py`` is a server that manages a YAML file that is supplied as a single argument to its command-line.

``manage_yaml.py`` uses the ``client/server`` model of ZeroMQ as the server.  Any clients should be implemented
using the client side of the ``client/server`` model of ZeroMQ.

``python manage_yaml.py [absolute_yaml_file_path]``

The ``absolute_yaml_file_path`` must be an absolute path to the YAML file, and you need to have write access
to it or ``manage_yaml.py`` will fail with an error.

If ``absolute_yaml_file_path`` is not specified, it defaults to ``/etc/status``.

``manage_yaml.py`` accepts requests to query or modify the given YAML file through a UNIX domain socket that
exists in the ``/tmp`` directory.  The socket has the same name as the absolute path of the YAML file, with the
slashes (``/``) replaced by underscores(``_``).  So, the UNIX socket used to manage the ``/etc/status`` file is
``/tmp/_etc_status``.

Requests to ``manage_yaml.py`` are also in YAML, and takes one of two forms

### Query Requests

A query request takes the form:

```
"QUERY":
    <key>:
        <key>:
            ...
            <key>:
    <key>:
        <key>:
            ...
            <key>:
    ...
```

Any given key at any level can have 0 or more subkeys.  If a given key doesn't exist in the managed YAML file,
it is ignored.

Any key for which there are no subkeys provided should be left with a ``null`` (blank) value.

``manage_yaml.py`` will return the same YAML with which it was provided, minus the ``QUERY`` key,
with the null-values of any given keys replaced by the actual values of these keys.

#### Example:

Suppose the file being managed (``/tmp/foo``), has the following content:

```yaml
"A":
    "one": 1
    "two": 2
    "three": 3
"B":
    "four": 4
    "five": 5
    "six": 6
```

The following query request:

```yaml
"QUERY":
    "A":
        "two":
        "twelve":
    "B":
```

will return:

```yaml
"A":
    "two": 2
"B":
    "four": 4
    "five": 5
    "six": 6
```

### Modify Requests

A modify request takes the form:

```
"modify":
    <key>:
        <key>:
            ...
            <key>: <new-value or null (blank)>
    <key>:
        <key>:
            ...
            <key>: <new-value or null (blank)>
    ...
```

Any given key at any level can have 0 or more subkeys.  If a given key doesn't exist in the managed YAML file,
it is either:
* added to the YAML file if it has a non-null value (and it is given the non-null value provided), or
* is ignored if it has a null value.

Any key that already exists in the YAML file either:
* has its current value replaced with the (non-null) ``new-value`` provided, or
* is removed from the YAML if the provided value is null

Modification requests return nothing.  To see newly modified key values, you'll need to submit a query request.

> IMPORTANT:  Every time a modification request is executed, the YAML file being managed by ``manage_yaml.py``
>   is updated on disk.

#### Example:

Suppose the file being managed (``/tmp/foo``), has the following content:

```yaml
"A":
    "one": 1
    "two": 2
    "three": 3
"B":
    "four": 4
    "five": 5
    "six": 6
```

The following modify request:

```yaml
"MODIFY":
    "A":
        "two": 200
        "twelve":
    "B":
        "four":
        "six": 66
        "seven": 7
```

will modify the YAML to be:

```yaml
"A":
    "one": 1
    "two": 200
    "three": 3
"B":
    "five": 5
    "six": 66
    "seven": 7
```

### The \_\_REPLACE__ Special Key

On a modification request, if for a given map you want to replace the entire map with only the keys given in the
request, i.e. rather than adding/modifying the values of the given keys in the map, specify the ``__REPLACE__`` key
along with the given keys.  The value of the ``__REPLACE__`` key is ignored.

#### Example:

Suppose the file being managed (``/tmp/foo``), has the following content:

```yaml
"A":
    "one": 1
    "two": 2
    "three": 3
"B":
    "four": 4
    "five": 5
    "six": 6
```

The following modify request:

```yaml
"MODIFY":
    "A":
        "__REPLACE__":
        "uno": 1
        "dos": 2
    "B":
        "four":
        "quatro": 4
        "seis": 6
        "six": 66
```

will modify the YAML to be:

```yaml
"A":
    "uno": 1
    "dos": 2
"B":
    "quatro": 4
    "five": 5
    "six": 66
    "seis": 6
```


## How to use interact_yaml.py

``interact_yaml.py`` is a client to a ``manage_yaml.py`` instance.  To connect to the ``manage_yaml.py`` instance
managing a particular YAML file, provided one exists and is running, specify the full absolute path of the
YAML file as a command-line argument to ``interact_yaml.py``:

``python manage_yaml.py [absolute_yaml_file_path]``

where ``absolute_yaml_file_path`` defaults to ``/etc/status``


``interact_yaml.py`` simple takes what is provided to it on its standard input, i.e. a query or modify request for
the managed YAML file, and passes it to the ``manage_yaml.py`` instance via a UNIX domain socket.

For the syntax of query and modify request, see above.

``interact_yaml.py`` then prints any response it gets from ``manage_yaml.py`` on its standard output.
