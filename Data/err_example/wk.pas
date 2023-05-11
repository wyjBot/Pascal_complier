program example(input,output);
    const pi = 3.14;
          e=2.73;
    var x,y:integer;
        z:array [3..9, 1..3] of char;
    function (x, y: boolean; var a,b:integer):integer;
        const pi = 3.14;
          e=2.73;
        begin
            if b then gcd:=a
            else gcd:=gcd(b, a mod b)
        end;
    begin
        z := 1;
        read(x, y);
        write(gcd(x, y))
    end.