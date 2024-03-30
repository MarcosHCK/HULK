-- Copyright 2021-2025
-- This file is part of HULK.
--
-- HULK is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- HULK is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with HULK.  If not, see <http://www.gnu.org/licenses/>.
--
generator ('python')

KEYWORD = 'as|base|break|elif|else|extends|for|function|if|in|inherits|is|let|new|protocol|return|self|type|while'

ADDITIVE_OPERATOR = '[-+]'
COMPARISION_OPERATOR = '[<>]|(<=)|(>=)|(==)|(!=)'
CONCAT_OPERATOR = '@@|@'
LOGICAL_OPERATOR = '[&|!]'
MULTIPLICATIVE_OPERATOR = '[*/%]'
POWER_OPERATOR = '^'

BOOLEAN_VALUE = 'false|true'
NUMBER_VALUE = '[0-9]+(\\.[0-9]+)?'
STRING_VALUE = '"(\\\\.|[^"])*"'

IDENTIFIER = '[a-zA-Z_][a-zA-Z_0-9]*'

ANNOTATE = ':'
ASSIGN = '='
COMMA = ','
CLASS_ACCESS = '\\.'
DESTRUCTIVE_ASSIGN = ':='
LAMBDA = '=>'

L_BRACKET = '[\\[]'
R_BRACKET = '[\\]]'
L_KEY = '[\\{]'
R_KEY = '[\\}]'
L_PARENTHESIS = '[\\(]'
R_PARENTHESIS = '[\\)]'
DOTCOM = ';'

IGNORE = '[ \t\n\r]'
