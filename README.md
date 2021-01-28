
# Router

This router is responsible for two things: Firstly, it routes requests for data
to correct endpoints.  Secondly, it handles caching of such requests.

At the system level, requests are often routed back to the router, asking for
RHS components of the data. This makes the router a central part of the data
negotiation process.

The fact that each separate request is cached is extremely important for
performance, as only absolutely necessary computations are performed.

The router itself is quite simple, it is its role in the system that makes it powerful.
