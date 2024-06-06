#pragma once

// Helper macro and methods for creating Enums which
// can be easily converted to/from strings.
//
// Declaration:
//
// e.g. ENUMS(FooBar, ENUMARGS(Foo, Bar), ENUMARGS("foo", "bar"))
//            ------           --------            ------------
//            Type name        Enumerators         String representations
//
// String conversion:
// e.g. const char* to_string(const FooBar& v);
//      bool from_string(const char* s, FooBar& v); // returns false on error
//
// Stream operators:
// e.g. FooBar fb;
//      std::cin >> fb;  // sets the badbit of the input stream on error
//

#include <array>
#include <cstdint>
#include <sstream>
#include <string>

#include <string.h>

namespace cmn {
namespace enums {
namespace details {

    template<typename ...Args>
    constexpr std::size_t va_count(Args&&...) { return sizeof...(Args); }

    template<std::size_t ...>
    struct max_len : std::integral_constant<std::size_t, 0> {};

    template<std::size_t X, std::size_t ... Xs>
    struct max_len<X, Xs...>
        : std::integral_constant<std::size_t, (X > max_len<Xs...>::value ? X : max_len<Xs...>::value)> {};

    template<typename ...Args>
    constexpr std::size_t va_max_len(Args&&...) { return max_len<sizeof(Args)...>::value; }

} // namespace details
} // namespace enums
} // namespace cmn

template<typename T> constexpr size_t enum_size() { return 0; }

//
// Macro Magic
//

#define ENUMARGS(...) __VA_ARGS__

#define ENUMS(NAME, VALUES, STRINGS)                                           \
    namespace enums{ namespace details { namespace NAME {                      \
        typedef std::array<                                                    \
            char[::cmn::enums::details::va_max_len(___ENUM_STRINGS(STRINGS))], \
            ::cmn::enums::details::va_count(___ENUM_STRINGS(STRINGS))          \
        > string_type_t;                                                       \
        constexpr size_t enum_size{::cmn::enums::details::va_count(STRINGS)};  \
        constexpr string_type_t strings{ ___ENUM_STRINGS(STRINGS) };           \
    }}}                                                                        \
    enum class NAME { ___ENUM_VALUES(VALUES) };                                \
    inline const char* to_string(NAME e) {                                     \
        return enums::details::NAME::strings[static_cast<size_t>(e)]; }        \
    inline bool from_string(const char* s, NAME& e) {                          \
        for (size_t n = 0; n < enums::details::NAME::enum_size; n++) {         \
            if (strcmp(s, enums::details::NAME::strings[n]) == 0) {            \
                e = static_cast<NAME>(n); return true; } }                     \
        e = static_cast<NAME>(enums::details::NAME::enum_size-1);              \
        return false; }                                                        \
    inline std::ostream& operator<<(std::ostream& s, NAME e) {                 \
        s << to_string(e); return s; }                                         \
    inline std::istream& operator>>(std::istream& s, NAME& e) {                \
        std::string r; s >> r;                                                 \
        if (!from_string(r.c_str(), e)) {                                      \
            s.setstate(std::ios_base::badbit); }                               \
        return s; }
/*
    NOTE:
    I would love to have this, but then we cant create enums in namespaces.
    The only thing i can think of right now, is to put everything into the
    global ::cmn::enums namespace and then typedef the enum type in the
    current one. But then we can't reuse the same name in different namespaces.

    template<> constexpr size_t enum_size<NAME>() {                         \
        return enums::details::NAME::strings.size(); }
*/

#define ___ENUM_VALUES(...) __VA_ARGS__, __unknown__
#define ___ENUM_STRINGS(...) __VA_ARGS__, "__unknown__"

//
// Utilities
//

namespace cmn {
namespace enums {

    template<typename T>
    void print_enumeration(std::ostream& os, size_t n)
    {
        os << static_cast<T>(n) << " (" << n << ")";
    }

    template<typename T>
    void print_enumerations(std::ostream& os)
    {
        if (enum_size<T>() > 0)
        {
            print_enumeration<T>(os, 0);

            for (size_t n = 1; n < enum_size<T>(); n++)
            {
                os << ", ";
                print_enumeration<T>(os, n);
            }
        }
    }

    template<typename T> struct print_enum {};

    template<typename T>
    inline std::ostream& operator<<(std::ostream& os, const print_enum<T>&)
    {
        print_enumerations<T>(os);
        return os;
    }

} // namespace enums
} // namespace cmn
