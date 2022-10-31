import logging
import time
import traceback


def display_start_time_passed_arguments_and_running_duration(func):
    def wrapper(*args, **kwargs):

        logging.info(f"Started {func.__name__:<50} | {args=}, {kwargs=}")

        start_time = time.time()

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logging.warning(
                f"Error in {func.__name__:<50} | {args=}, {kwargs=} | {repr(traceback.format_exc())}"
            )
            raise e

        took_secs = round(time.time() - start_time, 3)

        logging.info(
            f"{func.__name__:<50} | took {took_secs} seconds | {args=}, {kwargs=}"
        )

        return result

    return wrapper


def profile(wrapped_func):
    """
    simple decorator to profile functions, using cProfiler.
    usage:
        write @profile before function definition(decorate it with this function),
        after that use it to see results.
    """
    import functools

    @functools.wraps(wrapped_func)
    def wrapper_func(*args, **kwargs):
        import cProfile, pstats, io
        from pstats import SortKey

        pr = cProfile.Profile()
        pr.enable()

        res = wrapped_func(*args, **kwargs)

        pr.disable()
        s = io.StringIO()

        # sort by total function working time(not excluding other function call times from function) | "cumtime" column in normal output
        sort_by = SortKey.CUMULATIVE

        # # # or sort by specific function time(excluding other function call times from function) | "tottime" column in normal output
        # sort_by = SortKey.TIME

        ps = pstats.Stats(pr, stream=s).sort_stats(sort_by)

        # 20 - number of top lines to print
        ps.print_stats(20)
        logging.info(s.getvalue())

        return res

    return wrapper_func
