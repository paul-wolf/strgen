Progress Callback
=================

When using the ``progress_callback`` parameter of the ``render_list()``
method, it’s possible to inform others about the progress of string
generation. This is especially useful when generating a large number of
strings.

The callback function obtains two int parameters: ``(current, total)``,
which define the current progress and the total amount of requested
strings.

By using that, callers of ``render_list()`` are able to implement a
progress indicator suitable for informing end users about the progress
of string generation.
