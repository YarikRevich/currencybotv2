
class validators:

    @staticmethod
    def isfloat(messagetext):

        """
        Validator to check wether the entered text is appropriate

        """

        try:
            float(messagetext)
            if messagetext[2] == "." or messagetext[1] == ".":
                return True
        except ValueError:
            return False

    @staticmethod
    def isappropriate(range_from,range_to):

        """
        Validator to check whether the range(to) is not less than range(from)

        """
    
        if float(range_from) <= float(range_to):
            return True
        return False