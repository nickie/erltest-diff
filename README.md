erltest-diff
============

A tool that helps you compare the results of multiple runs
of the Erlang/OTP test suite.

    Usage: ./erltest-diff.py <URL-1> <URL-1>

    Examples:
       ./erltest-diff.py vanilla/ mine/
       ./erltest-diff.py http://erl.ang/tests/vanilla/ http://erl.ang/tests/mine/

    The two directory URLs should contain the index.html files produced
    when running ts:run().

The result of this script is a report similar to the following:

    $ ./erltest-diff.py http://erl.ang/tests/vanilla/ http://erl.ang/tests/mine/
    tests.runtime_tools_test
    < ok: 24, failed: 1, skipped: 1, user: 1, auto: 0, missing: 0
    > ok: 25, failed: 0, skipped: 1, user: 1, auto: 0, missing: 0

    < 26 system_information_SUITE  sanity_check FAILED {system_information_SUITE,sanity_check,268}{badmatch,{failed,[{missing_runtime_dependencies,"xmerl-1.3....}
    > 26 system_information_SUITE  sanity_check Ok 
    ------------------------------------------------------------------------
    tests.stdlib_test
    < ok: 1054, failed: 2, skipped: 6, user: 6, auto: 0, missing: 0
    > ok: 1053, failed: 3, skipped: 6, user: 6, auto: 0, missing: 0

    < 827 shell_SUITE  records FAILED {shell_SUITE,'-scan/1-fun-0-',2895}{badmatch,{error,{1,erl_parse,["syntax error before: ","'*'"...}
    > 827 shell_SUITE  records Ok 

    < 917 stdlib_SUITE  app_test Ok 
    > 917 stdlib_SUITE  app_test FAILED {stdlib_SUITE,app_test,71}suite_failed

    < 979 supervisor_SUITE  do_not_save_start_parameters_for_temporary_children Ok 
    > 979 supervisor_SUITE  do_not_save_start_parameters_for_temporary_children FAILED {supervisor_SUITE,dont_save_start_parameters_for_temporary_children,1363}{badmatch,false}

Explanation: In the first reported test (`runtime_tools`), the vanilla version fails one more test (`sanity_check` in the `system_information_SUITE`).  In the second reported test (`stdlib`), the vanilla version fails two tests and the alternative version fails three, but it's a bit more complicated as three tests are involved.
