#pragma once

#include <stdexcept>
#include <string>

#include <string.h>

#ifdef WIN32
#define strcasecmp(a,b) stricmp(a,b)
#endif

namespace config {

inline bool stob(const std::string& s)
{
    if (strcasecmp("true", s.c_str()) == 0)
    {
        return true;
    }
    if (strcasecmp("false", s.c_str()) == 0)
    {
        return false;
    }
    throw std::invalid_argument("s");
}

inline unsigned long long stohex(const std::string& s)
{
    return std::stoull(s, 0, 16);
}

template<typename T> T from_string(const std::string& s) { return T{}; }
template<typename T> T from_string(const std::string& s, int b) { return T{}; }

template<> std::string from_string<std::string>(const std::string& s) { return s; }

template<> float from_string<float>(const std::string& s) { return std::stof(s); }
template<> double from_string<double>(const std::string& s) { return std::stod(s); }
template<> long double from_string<long double>(const std::string& s) { return std::stold(s); }
template<> bool from_string<bool>(const std::string& s) { return stob(s); }

template<> char from_string<char>(const std::string& s) { return std::stoi(s); }
template<> short from_string<short>(const std::string& s) { return std::stoi(s); }
template<> int from_string<int>(const std::string& s) { return std::stoi(s); }
template<> long from_string<long>(const std::string& s) { return std::stol(s); }
template<> long long from_string<long long>(const std::string& s) { return std::stoll(s); }

template<> unsigned char from_string<unsigned char>(const std::string& s) { return std::stoul(s); }
template<> unsigned short from_string<unsigned short>(const std::string& s) { return std::stoul(s); }
template<> unsigned int from_string<unsigned int>(const std::string& s) { return std::stoul(s); }
template<> unsigned long from_string<unsigned long>(const std::string& s) { return std::stoul(s); }
template<> unsigned long long from_string<unsigned long long>(const std::string& s) { return std::stoull(s); }

template<> char from_string<char>(const std::string& s, int base) { return std::stoi(s, 0, base); }
template<> short from_string<short>(const std::string& s, int base) { return std::stoi(s, 0, base); }
template<> int from_string<int>(const std::string& s, int base) { return std::stoi(s, 0, base); }
template<> long from_string<long>(const std::string& s, int base) { return std::stol(s, 0, base); }
template<> long long from_string<long long>(const std::string& s, int base) { return std::stoll(s, 0, base); }

template<> unsigned char from_string<unsigned char>(const std::string& s, int base) { return std::stoul(s, 0, base); }
template<> unsigned short from_string<unsigned short>(const std::string& s, int base) { return std::stoul(s, 0, base); }
template<> unsigned int from_string<unsigned int>(const std::string& s, int base) { return std::stoul(s, 0, base); }
template<> unsigned long from_string<unsigned long>(const std::string& s, int base) { return std::stoul(s, 0, base); }
template<> unsigned long long from_string<unsigned long long>(const std::string& s, int base) { return std::stoull(s, 0, base); }

} // namespace config
