""" Driver for todo.txt parsing and balancing follows format defined at https://github.com/todotxt/todo.txt.  """
import todotxt
import unittest
import argparse

def arg_parser():
    """ Create an argument parser """
    parser = argparse.ArgumentParser(description="Utility for managing todo.txt files.")
    parser.add_argument("--test", help="Test the code.")
    parser.add_argument("--sort", nargs=1, help="Sort-by criterion. Can be repeated.",
                        choices=vars(todotxt.Todo()).keys(), action="append",
                        default=["creation_date", "priority", "due_date", "start_date", "description"])
    return parser


def test():
    """ Test parts of the package """
    unittest.main(module=todotxt)


def main():
    """ Do useful things with todo.txt files """
    parser = arg_parser()
    args = parser.parse_args()
    print(args)

    did_something = False
    if args.test:
        test()
        did_something = True
    if args.sort:
        did_something = True
    if not did_something:
        parser.print_help()


if __name__ == "__main__":
    main()
