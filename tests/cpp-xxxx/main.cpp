#include <iostream>
#include <string>
#include "config.hpp"

#define _PRINTLINE(cond, status, line) std::cout << '[' << line << "," status "] " cond "\n";
#define _TEST(cond, err, line) if (cond) { _PRINTLINE(#cond, "ok", line); } else { err += 1; _PRINTLINE(#cond, "!!", line); }
#define TEST(cond) _TEST(cond, errors, __LINE__)


int main(int argc, char** argv)
{
    const char* filename = "test.xxx";
    bool test_error = false;

    if (argc > 1)
    {
        filename = argv[1];
    }
    if (argc > 2)
    {
        if (std::string{argv[2]} == "error")
        {
            test_error = true;
        }
    }

    auto config = config::LoadConfig(filename);

    int errors = 0;

    TEST(config);

    TEST(config->types.am == -1);
    TEST(config->types.bm == -2);
    TEST(config->types.cm == -3);

    TEST(config->types.dm == 1);
    TEST(config->types.em == 2);

    TEST(config->types.fm == "asdf");

    TEST(config->types.gm == 1.3f);
    TEST(config->types.hm == 3.141592653589793d);

    TEST(config->types.im == true);
    TEST(config->types.jm == false);

    TEST(config->types.km.size() == 4);
    TEST(config->types.km[0] == 0);
    TEST(config->types.km[1] == 1);
    TEST(config->types.km[2] == 2);
    TEST(config->types.km[3] == 3);

    TEST(config->types.lm.size() == 4);
    TEST(config->types.lm[0] == "a");
    TEST(config->types.lm[1] == "b");
    TEST(config->types.lm[2] == "c");
    TEST(config->types.lm[3] == "d");

    TEST(config->types.mm.am == 4);

    TEST(config->types.nm.size() == 2);
    TEST(config->types.nm["foo"] == "bar");
    TEST(config->types.nm["bar"] == "foo");

    TEST(config->types.om.size() == 2);
    TEST(config->types.om[0].am == 0);
    TEST(config->types.om[1].am == 1);

    TEST(config->types.pm.size() == 2);
    TEST(config->types.pm[101].am == 1);
    TEST(config->types.pm[102].am == 2);

    return errors;
}
