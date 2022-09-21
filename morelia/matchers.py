r"""
Steps
=====

.. _matching-steps:

Matching steps
--------------

When Morelia executes steps described in feature files it looks
inside passed :py:class:`unittest.TestCase` object and search for methods
which name starts with `step_`. Then it selects correct method using:

* `Regular expressions`_
* `Format-like strings`_
* `Method names`_

If you look in example from :ref:`usage-guide`:

.. code-block:: python

    # test_acceptance.py

    from pathlib import Path
    import unittest

    from morelia import verify


    class CalculatorTestCase(unittest.TestCase):

        def test_addition(self):
            ''' Addition feature '''
            filename = Path(__file__) / "calculator.feature"
            verify(filename, self)

        def step_I_have_powered_calculator_on(self):
            r'I have powered calculator on'
            self.stack = []

        def step_I_enter_a_number_into_the_calculator(self, number):
            r'I enter "(\d+)" into the calculator'  # match by regexp
            self.stack.append(int(number))

        def step_I_press_add(self):  #  matched by method name
            self.result = sum(self.stack)

        def step_the_result_should_be_on_the_screen(self, number):
            r'the result should be "{number}" on the screen'  # match by format-like string
            self.assertEqual(int(number), self.result)

You'll see three types of matching.

Regular expressions
^^^^^^^^^^^^^^^^^^^

Method ``step_I_enter_number_into_the_calculator`` from example is matched
by :py:mod:`regular expression <re>` as it's docstring

.. code-block:: python

        r'I enter "(\d+)" into the calculator'

matches steps:

.. code-block:: cucumber

        When I enter "50" into the calculator
        And I enter "70" into the calculator

Regular expressions, such as ``(\d+)``, are expanded into positional step arguments,
such as ``number`` in above example. If you would use named groups like ``(?P<number>\d+)``
then capttured expressions from steps will be put as given keyword argument to method.

Remember to use tight expressions, such as ``(\d+)``,
not expressions like ``(\d*)`` or ``(.*)``, to validate your input.

Format-like strings
^^^^^^^^^^^^^^^^^^^

Method ``step_the_result_should_be_on_the_screen`` from example is matched
by :ref:`format-like strings <python:formatspec>` as it's docstring

.. code-block:: python

        r'the result should be "{number}" on the screen'

matches step:

.. code-block:: cucumber

        Then the result should be "120" on the screen

Method names
^^^^^^^^^^^^

Method ``step_I_press_add`` from example is matched by method name which matches
step:

.. code-block:: cucumber

        And I press add

Choosing which matchers to use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default morelia search for methods using in order:

- format-like strings matcher ("parse" matcher)
- regex matcher ("regex" matcher)
- method names matcher ("method" matcher)

You can override it in your pyproject.toml file. E.g.:

.. code-block:: toml

    [tool.morelia.default]
    matchers=["regex", "parse"]

.. _matching-tables:

Tables
------

If you use Scenarios with tables and `<angles>` around the payload variable names:

.. code-block:: cucumber

    Scenario: orders above $100.00 to the continental US get free ground shipping
      When we send an order totaling $<total>, with a 12345 SKU, to our warehouse
       And the order will ship to <destination>
      Then the ground shipping cost is $<cost>
       And <rapid> delivery might be available

           |  total | destination            |  cost | rapid |

           |  98.00 | Rhode Island           |  8.25 |  yes  |
           | 101.00 | Rhode Island           |  0.00 |  yes  |
           |  99.00 | Kansas                 |  8.25 |  yes  |
           | 101.00 | Kansas                 |  0.00 |  yes  |
           |  99.00 | Hawaii                 |  8.25 |  yes  |
           | 101.00 | Hawaii                 |  8.25 |  yes  |
           | 101.00 | Alaska                 |  8.25 |  yes  |
           |  99.00 | Ontario, Canada        | 40.00 |   no  |
           |  99.00 | Brisbane, Australia    | 55.00 |   no  |
           |  99.00 | London, United Kingdom | 55.00 |   no  |
           |  99.00 | Kuantan, Malaysia      | 55.00 |   no  |
           | 101.00 | Tierra del Fuego       | 55.00 |   no  |

then that Scenario will unroll into a series of scenarios,
each with one value from the table inserted into their placeholders `<total>`,
`<destination>`, and `<rapid>`.
So this step method will receive each line in the "destination" column:

.. code-block:: python

    def step_the_order_will_ship_to_(self, location):
        r'the order will ship to (.*)'

(And observe that naming the placeholder the same as the method argument
is a *reeeally* good idea, but naturally unenforceable.)

Morelia will take each line of the table,
and construct a complete test case out of the Scenario steps,
running :py:meth:`unittest.TestCase.setUp()` and :py:meth:`unittest.TestCase.tearDown()` around them.

If you use many tables then Morelia would use permutation of all rows in all tables:

.. code-block:: cucumber

    Scenario: orders above $100.00 to the continental US get free ground shipping
      When we send an order totaling $<total>, with a 12345 SKU, to our warehouse
       And the order will ship to <destination>
       And we choose that delivery should be <speed>
            | speed   |

            | rapid   |
            | regular |

      Then the ground shipping cost is $<cost>

           |  total | destination            |  cost |

           |  98.00 | Rhode Island           |  8.25 |
           | 101.00 | Rhode Island           |  0.00 |
           |  99.00 | Kansas                 |  8.25 |

In above example 2 * 3 = 6 different test cases would be generated.

.. _matching-docstrings:

Doc Strings
-----------

Docstrings attached to steps are passed as keyword argument `_text` into
method:

.. code-block:: cucumber

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers

    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then I would see on the screen
            '''
            Calculator example
            ==================
             50
            +70
            ---
            120
            '''

.. code-block:: python

   def step_i_would_see_on_the_screen(self, _text):
        pass

   # or

   def step_i_would_see_on_the_screen(self, **kwargs):
        _text = kwargs.pop('_text')

Morelia is smart enough not to passing this argument if you don't name it.
Below example won't raise exception:

.. code-block:: python

   def step_i_would_see_on_the_screen(self):
        pass

It'll be simply assumed that you ignore docstring.

.. _labels-matching:

Labels
------

Labels attached to features and scenarios are available as keyword argument `_label`:

.. code-block:: cucumber

    @web
    @android @ios
    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers

    @wip
    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then the result should be "120" on the screen

.. code-block:: python

   def step_I_enter_number_into_the_calculator(self, num, _label):
        pass

As like with doc-strings you can ommit keyword parameter if you don't need it:

.. code-block:: python

   def step_I_enter_number_into_the_calculator(self, num):
        pass

Labels allows you to implement custom logic depending on labels given.

.. note:: **Compatibility**

   Morelia does not connects any custom logic with labels as some other
   Behavior Driven Development tools do. You are put in the charge and should
   add logic if any. If you are looking for ability to selectivly running
   features and scenarios look at :py:func:`morelia.decorators.tags` decorator.

Matchers Classes
----------------
"""

import re
import unicodedata
from abc import ABCMeta, abstractmethod

import parse

PAT = "(^step_|^given_|^when_|^then_)"


class IStepMatcher:
    """Matches methods to steps.

    Subclasses should implement at least `match` and `suggest` methods.
    """

    __metaclass__ = ABCMeta

    def __init__(self, suite, step_pattern=PAT):
        self._suite = suite
        self._matcher = re.compile(step_pattern)
        self._next = None

    def _get_all_step_methods(self):
        match = self._matcher.match
        return [method_name for method_name in dir(self._suite) if match(method_name)]

    def add_matcher(self, matcher):
        """Add new matcher at end of CoR.

        :param IStepMatcher matcher: matcher to add
        :returns: self
        """
        if self._next is None:
            self._next = matcher
        else:
            self._next.add_matcher(matcher)
        return self

    def find(self, predicate, augmented_predicate, step_methods=None):
        if step_methods is None:
            step_methods = self._get_all_step_methods()
        method, args, kwargs = self.match(predicate, augmented_predicate, step_methods)
        if method:
            return method, args, kwargs
        if self._next is not None:
            return self._next.find(predicate, augmented_predicate, step_methods)
        return None, (), {}

    @abstractmethod
    def match(self, predicate, augmented_predicate, step_methods):
        """Match method from suite to given predicate.

        :param str predicate: step predicate
        :param str augmented_predicate: step augmented_predicate
        :param list step_methods: list of all step methods from suite
        :returns: (method object, args, kwargs)
        :rtype: (method, tuple, dict)
        """
        pass  # pragma: nocover

    def suggest(self, predicate, prefix="step"):
        """Suggest method definition.

        Method is used to suggest methods that should be implemented.

        :param str predicate: step predicate
        :returns: (suggested method definition, suggested method name, suggested docstring)
        :rtype: (str, str, str)
        """
        docstring, extra_arguments = self._suggest_doc_string(predicate)
        with open("/tmp/test.py", "w") as f:
            f.write(str(extra_arguments))
        method_name = self.slugify(predicate)
        suggest = "    def {prefix}_{method_name}(self{args}):\n        {docstring}\n\n        raise NotImplementedError('{predicate}')\n\n".format(
            prefix=prefix,
            method_name=method_name,
            args=extra_arguments,
            docstring=docstring,
            predicate=predicate.replace("'", "\\'"),
        )
        return suggest, method_name, docstring

    def _suggest_doc_string(self, predicate):
        predicate = predicate.replace("'", r"\'").replace("\n", r"\n")

        arguments = self._add_extra_args(r'["\<](.+?)["\>]', predicate)
        arguments = self._name_arguments(arguments)

        predicate = self.replace_placeholders(predicate, arguments)
        predicate = re.sub(r" \s+", r"\\s+", predicate)

        arguments = self._format_arguments(arguments)
        return "r'%s'" % predicate, arguments

    def _name_arguments(self, extra_arguments):
        if not extra_arguments:
            return ""
        arguments = []
        number_arguments_count = sum(
            1 for arg_type, arg in extra_arguments if arg_type == "number"
        )
        if number_arguments_count < 2:
            num_suffixes = iter([""])
        else:
            num_suffixes = iter(range(1, number_arguments_count + 1))

        for arg_type, arg in extra_arguments:
            if arg_type == "number":
                arguments.append("number%s" % next(num_suffixes))
            else:
                arguments.append(arg)
        return arguments

    def _format_arguments(self, arguments):
        if not arguments:
            return ""
        return ", " + ", ".join(arguments)

    def replace_placeholders(self, predicate, arguments):
        predicate = re.sub(r'".+?"', '"([^"]+)"', predicate)
        predicate = re.sub(r"\<.+?\>", "(.+)", predicate)
        return predicate

    def _add_extra_args(self, matcher, predicate):
        args = re.findall(matcher, predicate)
        result = []
        for arg in args:
            try:
                float(arg)
            except ValueError:
                arg = ("id", self.slugify(arg))
            else:
                arg = ("number", arg)
            result.append(arg)
        return result

    def slugify(self, predicate):
        result = []
        for part in re.split(r"[^\w]+", predicate):
            part = (
                unicodedata.normalize("NFD", part)
                .encode("ascii", "replace")
                .decode("utf-8")
            )
            part = part.replace("??", "_").replace("?", "")
            try:
                float(part)
            except ValueError:
                pass
            else:
                part = "number"
            result.append(part)
        return "_".join(result).strip("_")


class MethodNameStepMatcher(IStepMatcher):
    """Matcher that matches steps by method name."""

    def match(self, predicate, augmented_predicate, step_methods):
        """See :py:meth:`IStepMatcher.match`."""
        matches = self.__find_matching_methods(step_methods, predicate)
        return self.__select_best_match(matches)

    def __find_matching_methods(self, step_methods, predicate):
        clean = re.sub(r"[^\w]", "_?", predicate)
        pattern = PAT + clean + "$"
        regexp = re.compile(pattern)
        for method_name in step_methods:
            if regexp.match(method_name):
                method = self._suite.__getattribute__(method_name)
                yield (method, (), {})

    def __select_best_match(self, matches):
        try:
            best_match = next(iter(matches))
        except StopIteration:
            return None, (), {}
        else:
            method, args, kwargs = best_match
            return method, args, kwargs

    def suggest(self, predicate, prefix="step"):
        """See :py:meth:`IStepMatcher.suggest`."""
        method_name = self.slugify(predicate)
        suggest = "    def {prefix}_{method_name}(self):\n\n        raise NotImplementedError('{predicate}')\n\n".format(
            prefix=prefix, method_name=method_name, predicate=predicate.replace("'", "\\'")
        )
        return suggest, method_name, ""

    def slugify(self, predicate):
        predicate = (
            unicodedata.normalize("NFD", predicate)
            .encode("ascii", "replace")
            .decode("utf-8")
        )
        predicate = predicate.replace("??", "_").replace("?", "")
        return re.sub(r"[^\w]+", "_", predicate, re.U).strip("_")


class RegexpStepMatcher(IStepMatcher):
    """Matcher that matches steps by regexp in docstring."""

    def match(self, predicate, augmented_predicate, step_methods):
        """See :py:meth:`IStepMatcher.match`."""
        matches = self.__find_matching_methods(step_methods, augmented_predicate)
        return self.__select_best_match(matches)

    def __find_matching_methods(self, step_methods, augmented_predicate):
        for method, doc in self.__find_methods_with_docstring(step_methods):
            doc = re.compile("^" + doc + "$")
            match = doc.match(augmented_predicate)
            if match:
                kwargs = match.groupdict()
                if not kwargs:
                    args = match.groups()
                else:
                    args = ()
                yield (method, args, kwargs)

        return None, (), {}

    def __find_methods_with_docstring(self, step_methods):
        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            doc = method.__doc__
            if doc:
                yield method, doc

    def __select_best_match(self, matches):
        try:
            best_match = next(iter(matches))
        except StopIteration:
            return None, (), {}
        else:
            method, args, kwargs = best_match
            return method, args, kwargs


class ParseStepMatcher(IStepMatcher):
    """Matcher that matches steps by format-like string in docstring."""

    def match(self, predicate, augmented_predicate, step_methods):
        """See :py:meth:`IStepMatcher.match`."""
        matches = self.__find_matching_methods(step_methods, augmented_predicate)
        return self.__select_best_match(matches)

    def __find_matching_methods(self, step_methods, augmented_predicate):
        for method, doc in self.__find_methods_with_docstring(step_methods):
            match = parse.parse(doc, augmented_predicate)
            if match:
                args = match.fixed
                kwargs = match.named
                yield (len(args) + len(kwargs), method, tuple(args), kwargs)

    def __find_methods_with_docstring(self, step_methods):
        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            doc = method.__doc__
            if doc:
                yield method, doc

    def __select_best_match(self, matches):
        matches = sorted(matches, reverse=True)
        try:
            best_match = next(iter(matches))
        except StopIteration:
            return None, (), {}
        else:
            _, method, args, kwargs = best_match
            return method, args, kwargs

    def replace_placeholders(self, predicate, arguments):
        arguments = iter(arguments)

        def repl(match):
            if match.group(0).startswith('"'):
                return '"{%s}"' % next(arguments)
            return "{%s}" % next(arguments)

        predicate = re.sub(r'".+?"|\<.+?\>', repl, predicate)
        return predicate
