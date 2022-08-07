"""Mini-version of Reverso context with command-line interface."""

from reverso_api.context import ReversoContextAPI
import time

def highlight_example(text, highlighted):
    """'Highlights' ALL the highlighted parts of the word usage example with * characters.
    Args:
        text: The text of the example
        highlighted: Indexes of the highlighted parts' indexes
    Returns:
        The highlighted word usage example
    """

    def insert_char(string, index, char):
        """Inserts the given character into a string.
        Example:
            string = "abc"
            index = 1
            char = "+"
            Returns: "a+bc"
        Args:
            string: Given string
            index: Index where to insert
            char: Which char to insert
        Return:
            String string with character char inserted at index index.
        """

        return string[:index] + char + string[index:]

    def highlight_once(string, start, end, shift):
        """'Highlights' ONE highlighted part of the word usage example with two * characters.
        Example:
            string = "This is a sample string"
            start = 0
            end = 4
            shift = 0
            Returns: "*This* is a sample string"
        Args:
            string: The string to be highlighted
            start: The start index of the highlighted part
            end: The end index of the highlighted part
            shift: How many highlighting chars were already inserted (to get right indexes)
        Returns:
            The highlighted string.
        """

        s = insert_char(string, start + shift, "`")
        s = insert_char(s, end + shift + 1, "`")
        return s

    shift = 0
    for start, end in highlighted:
        text = highlight_once(text, start, end, shift)
        shift += 2
    return text



start_time = time.time()

api = ReversoContextAPI("chair", "", "en", "ru")
try:
    print(list(map(lambda x: x.translation, sorted(api.get_translations(), key=lambda x: -x.frequency))))
except Exception as e:
    print(e)

# print("--- %s seconds ---" % (time.time() - start_time))
# start_time = time.time()

print(list(api.get_translations()))

# print("--- %s seconds ---" % (time.time() - start_time))
# start_time = time.time()

# a = sorted(api.get_translations(), key=lambda x: -x.frequency)[:5]

# print("--- %s seconds ---" % (time.time() - start_time))

# print()
# print("Translations:")

print(list(map(lambda x: x.translation, sorted(api.get_translations(), key=lambda x: -x.frequency)[:5])))

print(list(map(lambda x: x.translation, sorted(api.get_translations(), key=lambda x: -x.frequency))))

# # for source_word, translation, frequency, _, _ in sorted(api.get_translations(), key=lambda x: -x.frequency)[:5]:
# #     print(source_word, "==", translation)

# print()
# print("Word Usage Examples:")
# examples_num = 0
# examples = []
# start_time = time.time()
# for source, _ in api.get_examples():
#     examples.append(highlight_example(source.text, source.highlighted))
#     examples_num += 1
#     if examples_num == 20:
#         break
# print("--- %s seconds ---" % (time.time() - start_time))
# print(examples)