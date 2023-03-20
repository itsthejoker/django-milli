# django-milli

Have you ever stared at your database and thought, "how in the world am I going to implement this fuzzy / ranked search performantly?" I certainly have, and after days of carefully tuning my query to get it to something I could live with, I implemented [Meilesearch](https://docs.meilisearch.com/) and promptly watched my worries wash away as search results were returned in the tens of milliseconds. However, Meilesearch isn't the right choice for every project:

* You need to run the full Meilesearch server -- another docker container to manage
* HTTP-based communication to and from Meilesearch is another round trip that has to be made

What if you could get the primary benefit of Meilesearch (hilariously fast search) without running another server / container? Nothing comes for free, so here's the tradeoff:

* you can only index one collection of data
* no filtering -- only searching

But you also get a self-contained thing, Python bindings, and a Django app that works out of the box. Not too bad of a trade depending on what you need. The magic behind this is https://github.com/AlexAltea/milli-py, which adds the Python bindings, and this package, `django-milli`, wraps `milli-py` and allows automatic (or mostly automatic) management of a search cache that automatically returns a list of your model, all ready to go!

`django-milli` uses signals and `milli-py` to keep an up-to-date search cache available for you at all times -- just call it with the search term:

```python
from django_milli import search

results = search("Hi")
print(results)
[<Person: Hi>, <Person: Hi!>, <Person: hiiiii>]
```

Notice that this is not a QuerySet. That's because Milli returns the search responses in an ordered fashion based on how accurate the response is, but you can't get that in Django because there's not an easy way to express that to the database. Instead, `django-milli` reorders the queryset into a list so that the order of objects you get back are in the same order we expect. This may have performance concerns on vague searches, so you also have the option to just request the "bare" results back from Milli:

```python
from django_milli import search

results = search("Hi", return_queryset=False)
print(results)
[{'id': 10, 'name': 'Hi'}, {'id': 11, 'name': 'Hi!'}, {'id': 2, 'name': 'hiiiii'}]
```

However, remember that just shoving those IDs into Django will result in an _unordered QuerySet_, so you have to figure out what to do with that next.

## Installation

You will need the Rust toolchain -- [get the command from here](https://www.rust-lang.org/tools/install)! Installing with `pip` looks like this:

~~pip install django-milli~~ Until `milli-py 1.0.1` is released, you can only get this from GitHub releases due to security restrictions on PyPI preventing listing dependencies that are on GitHub. Sorry!

NOTE: You _may_ have issues installing this with Poetry due to a bug where git submodules aren't parsed correctly. A proposed fix has been added and should be released in Poetry 1.4.2 (we are on 1.4.1 as of this writing).

## Configuration

`django-milli` has a bunch of settings that you can configure, though I strived to make the defaults sane. There's also one optional middleware that handles creating the index for you if you don't want to do it manually. Each of these keys go at the root of your `settings.py` file.

### MILLI_INDEX_MODEL_SETTINGS

This is the only config you have to set. This is a dict of options, where those options look like this:

```python
MILLI_INDEX_MODEL_SETTINGS = {
    'model': 'myapp.models.MyFavoritePeople',
    'fields': ['name']
}
```

This example also uses the default behavior of `MILLI_AUTO_ADD_ID_FIELD`, so the final field list will actually be `['id', 'name']` -- if that's not the behavior you want, you'll need to flip that switch. See below for details.

### MILLI_DB_SIZE

Default: 2GB

Optionally change the default size allocated to the cache database. By default, it allocates 2GB of space (according to the milli-py author, the entirety of IMDb is ~1.1GB when loaded) though you can override this if you need. The size is in bytes, so specify it like this: `2 ** 30 * X` where `X` is the number of gigabytes you want to assign. Or do less than that. Up to you.

### MILLI_DB_FOLDER

Default: `BASE_DIR`

Milli will create two files: a `data.mdb` and a `lock.mdb` file. This allows you to specify the folder where those files spawn; if you don't specify, they'll appear in your server root.

### MILLI_AUTO_ADD_ID_FIELD

Default: `True`

Makes it so that your `fields` list automatically includes the `id` attribute from your model. Some folks might not want this, but searching might not work correctly if you don't pass the `id` field at all. This is more of a safety net than anything.

### MILLI_NO_LOGGING

Default: `False`

For the handful of times where Milli might put something in your logs, you can disable it entirelly by setting this to `True`.

## Middleware

`django-milli` contains one piece of middleware that looks like this:

```python
MIDDLEWARE = [
    ...,
    "django_milli.middleware.MilliStartupMiddleware",
]
```

This middleware acts in conjunction with the following two settings:

### MILLI_BUILD_CACHE_ON_SERVER_START

Default: `True`

With the above middleware installed, Milli will automatically create the search cache when you start the server if a cache does not already exist. This is usually a fairly quick operation and if you don't have a ton of data, it is recommended to leave this on.

### MILLI_REBUILD_CACHE_ON_SERVER_START

Default: `True`

Only a few characters different, this will blow away the cache and rebuild it if the cache already exists when the server starts. You might not need this functionality, so you can always toggle this one.

## Manually Building the Cache

If you don't want to build the cache automatically, maybe because you want to pass in a specific queryset to start the cache from, then do not configure the `MilliStartupMiddleware` -- you're going to need this:

```python
from django_milli import build_index

queryset = MyModel.objects.filter(stuff=True)

build_index(custom_queryset=queryset)
# OR, to wipe a pre-existing cache
build_index(custom_queryset=queryset, remove_existing=True)
```

You can tuck that into a management command if you need.

## Ending Thoughts

This is not as full-featured as the full Meilesearch -- if you need filters, pagination, or other advanced features, you'll want to check out their full-sized product. This is just a bite-sized version that lets you get rolling if you _don't_ need all those features. Good luck!