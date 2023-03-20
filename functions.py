#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By: CheerfulAnt (Github account holder) <CheerfulAnt@outlook.com>
# License: MIT License.
# ---------------------------------------------------------------------------
""" This script is part of the lotto-2023-db project.
    *Just import from old project, some functions will be replaced
    by NumPy or pandas in the near future.*
    """
# ---------------------------------------------------------------------------

# sums digits from date (year, month day), date can be with non digits characters

def draw_date_sum(date_in):
    numbers_sum = 0

    for char in date_in:
        if char.isdigit():
            numbers_sum += int(char)
    return numbers_sum


# sums recursively digits until one digit is found, if it finds "master number"
# it returns them instead of the sum of all
# to work needs the draw_date_sum function and date as a parameter

def master(date_in, draw_date_sum_in):
    master_number = ['11', '22', '33', '44', '55']

    if len(str(date_in)) > 1:

        date_in = str(draw_date_sum_in(date_in))  # return sum of data digits

        if date_in in master_number:

            return int(date_in)
        else:
            return master(date_in, draw_date_sum_in)

    if len(str(date_in)) == 1:
        return int(date_in)


# returns True if year is leap, otherwise False, with no checking if year is before 1582

def leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        return True
    else:
        return False


# returns median

def median(values, values_amount=6):
    if values_amount % 2 == 0:
        median = (values[int(values_amount / 2) - 1] + (values[int(values_amount / 2)])) / 2
    else:
        median = values[int((values_amount + 1) / 2) - 1]
    return median

# prime number test

def prime(number_in):

    i = 2
    square_root_number = number_in**(1/2)

    if number_in == 1:
        return 0

    while  i <= square_root_number:

        if not (number_in % i):
            return 0
        i += 1

    return 1


# prime numbers counter


def prime_counter(numbers_list_in, prime_in):

    counter_in = 0

    for number_in in numbers_list_in:

        if prime_in(number_in):
            counter_in += 1

    return counter_in