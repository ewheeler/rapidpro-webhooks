import functools
import time
import uuid

from flask import copy_current_request_context, g, jsonify, request

import gevent
import redis

from rapidpro_webhooks.apps.core import exceptions

r = redis.Redis()


def limit(max_requests=100, period=60, by="ip", group=None):
    if not callable(by):
        by = {'ip': lambda: request.remote_addr}[by]

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            group = kwargs.get('group') or request.endpoint
            key = ":".join(["rl", group, by() or '127.0.0.1'])

            try:
                remaining = max_requests - int(r.get(key))
            except (ValueError, TypeError):
                remaining = max_requests
                r.set(key, 0)

            ttl = r.ttl(key)
            if not ttl:
                r.expire(key, period)
                ttl = period

            g.view_limits = (max_requests, remaining - 1, time.time() + ttl)

            if remaining > 0:
                r.incr(key, 1)
                return f(*args, **kwargs)
            else:
                raise exceptions.RateLimitError()
        return wrapped
    return decorator


def background(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        jobid = uuid.uuid4().hex
        key = 'job-{0}'.format(jobid)
        skey = 'job-{0}-status'.format(jobid)
        expire_time = 3600
        r.set(skey, 202)
        r.expire(skey, expire_time)

        @copy_current_request_context
        def task():
            try:
                data = f(*args, **kwargs)
            except BaseException:
                r.set(skey, 500)
            else:
                r.set(skey, 200)
                r.set(key, data)
                r.expire(key, expire_time)
            r.expire(skey, expire_time)

        gevent.spawn(task)
        return jsonify({"job": jobid})
    return wrapper
