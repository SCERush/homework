#include <iostream>
#include <algorithm>
// #include <bits/stdc++.h>
#include <cmath>
#include <bitset>
#include <string>
#include <stdio.h>
#include <stdlib.h>

using namespace std;

string str2bin(string text)
{
    string res = "";
    for (int i = 0; i < text.length(); i++)
    {
        bitset<8> bits(text[i]);
        res += bits.to_string();
    }
    return res;
}

string bin2hex(string text)
{
    char arr[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
    int frac[4];
    frac[0] = 1;
    for (int i = 1; i < 4; i++)
        frac[i] = frac[i - 1] * 2;
    string res = "";
    reverse(text.begin(), text.end());
    string _text = text;

    int ln = (int)_text.size();
    for (int i = 0; i < ln; i += 4)
    {
        int ans = 0;
        for (int j = 0; j < 4; j++)
        {
            if (i + j >= ln)
                break;
            int tmp = _text[i + j] - '0';
            tmp *= frac[j];
            ans += tmp;
        }
        res += arr[ans];
    }

    reverse(res.begin(), res.end());
    return res;
}

string hex2bin(string text)
{
    string res = "";
    int ln = (int)text.size();

    for (int i = 0; i < ln; i++)
    {
        int tmp = 0;
        if (text[i] >= '0' && text[i] <= '9')
            tmp = text[i] - '0';
        else
            tmp = text[i] - 'A' + 10;
        string ans = "";
        for (int j = 3; j >= 0; j--)
        {
            int pbit = 1 << j;
            if (tmp & pbit)
                ans += '1';
            else
                ans += '0';
        }
        res += ans;
    }
    return res;
}

string bin2str(string text)
{
    string res = "";
    for (int i = 0; i < text.length(); i += 8)
    {
        int num = 0;
        for (int j = i; j < i + 8; j++)
        {
            num += (text[j] - '0') * pow(2, i + 7 - j);
        }
        res += num;
    }
    return res;
}

int main()
{
    char flag;
    cout << "Please choose the mode : \n0.exit \n1.encrypt \n2.decrypt" << endl;
    cin >> flag;

    while (flag != '0')
    {
        if (flag == '1')
        {
            // encode
            string plain;
            string key;
            cout << "Please input the plain text : " << endl;
            getchar();
            getline(cin, plain);
            cout << "Please input the key (the key must be 8 charests) : " << endl;
            cin >> key;
            while (plain.length() % 8 != 0)
                plain += " ";
            if (key.length() != 8)
            {
                cout << "The key must be 8 charests!!!" << endl;
                continue;
            }

            // cout << plain << endl;
            string _plain = str2bin(plain);
            string _key = str2bin(key);
            // string cipher = CBC(_plain, key, en);
            // bin2hex
        }
        else if (flag == '2')
        {
            // decode
            string cipher;
            string key;
            cout << "Please input the cipher text : " << endl;
            cin >> cipher;
            cout << "Please input the key (the key must be 8 charests) : " << endl;
            cin >> key;
            if (key.length() != 8)
            {
                cout << "The key must be 8 charests!!!" << endl;
                continue;
            }

            string _cipher = hex2bin(cipher);
            string _key = str2bin(key);
            // string plain = CBC(_cipher, key, de);
            // bin2str
        }
        else
        {
            cout << "Wrong number!!!" << endl;
        }
        cin >> flag;
    }

    // string str = "ABC";
    // string str0 = str2bin(str);
    // string str1 = bin2hex(str0);
    // string str2 = hex2bin(str1);
    // string str3 = bin2str(str2);
    // cout << "str : " << str << endl;
    // cout << "str -> bin : " << str0 << endl;
    // cout << "bin -> hex : " << str1 << endl;
    // cout << "hex -> bin : " << str2 << endl;
    // cout << "bin -> str : " << str3 << endl;
    return 0;
}