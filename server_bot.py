import discord, random, time, random, openpyxl
from discord.ext import commands

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all()) # '$' 명령어 인자
TOKEN = "****" # 토큰 입력

# 엑셀 읽고 인원 정보 리스트에 담기 (엑셀 새로고침)
def settings():
    global db, ws
    db = openpyxl.load_workbook("database_example.xlsx") # 데이터베이스 엑셀 파일
    ws = db["Sheet1"] # Sheet1 데이터베이스 사용 (Sheet2는 백업용)
    global members, members_attend, members_code, members_id, members_point, members_warn
    members = [] # 마인크래프트 닉네임
    members_id = [] # 디스코드 사용자 ID
    members_code = [] # 디스코드 사용자 Code (ex. #0000) - 사용 안 함
    members_warn = [] # 경고 누적 횟수
    members_attend = [] # 출석 가능 날짜
    members_point = [] # 포인트 정보
    # endpoint 사용자 등장할 때까지 사용자 입력
    i = 2
    while i:
        members.append(ws['A'+str(i)].value)
        members_id.append(ws['B'+str(i)].value)
        members_code.append(ws['C'+str(i)].value)
        members_point.append(ws['E'+str(i)].value)
        members_warn.append(ws['F'+str(i)].value)
        members_attend.append(ws['G'+str(i)].value)
        i += 1
        if str(ws['A'+str(i)].value) == 'endpoint': break
    

# 엑셀 로딩
settings()

# 엑셀 로드 확인 로그
print("Minecraft NickName:", end='')
print(members)
print("Discord ID:", end='') 
print(members_id)
print("Point:", end='') 
print(members_point)
print("Warn:", end='')
print(members_warn)
print("Attendable Date:", end='')
print(members_attend)
print("Excel Database Successfully Loaded. ("+ time.strftime('%c', time.localtime(time.time())) + ")")
db.close()

# 등록
@bot.command(name="등록")
async def register(ctx, text):
    settings()
    print(text)
    # 디스코드 아이디 등록된 경우 (이미 등록된 경우)
    if str(ctx.author.id) in members_id:
        embed = discord.Embed(title="오류",
                            description = "등록 오류가 발생했습니다.",
                            color=0xC8D7FF)
        embed.add_field(name="이미 등록된 사용자", value=ctx.author.name+"님은 이미 등록된 사용자입니다.\n계속해서 문제가 발생한다면 문의하세요.")
        await ctx.channel.send(embed=embed)
        print("[ERROR] "+ctx.author.name+"is already member. ("+time.strftime('%c', time.localtime(time.time()))+")")
    #디스코드 아이디 등록 안 된 경우
    else:
        # 마인크래프트만 등록된 경우 (업데이트 등록)
        if text in members:
            ws['B'+str(members.index(text)+2)] = str(ctx.author.id)
            ws['C'+str(members.index(text)+2)] = '' # 사용 안 함
            ws['E'+str(members.index(text)+2)] = 0
            ws['F'+str(members.index(text)+2)] = 0
            ws['G'+str(members.index(text)+2)] = int(time.strftime('%d', time.localtime(time.time())))
            embed = discord.Embed(title="등록 완료",
                    description = str(ctx.author.name) + "님이 등록되었습니다.",
                    color=0xC8D7FF)
            await ctx.channel.send(embed=embed)
            print(ctx.author.name+"became member successfully. ("+time.strftime('%c', time.localtime(time.time()))+")")
            print("[UPDATED] Minecraft Nickname: "+ctx.author.name+"/ Discord User ID: "+ctx.author.id+" ("+time.strftime('%c', time.localtime(time.time()))+")")
        # 마인크래프트, 디스코드 모두 등록 안 된 경우 (신규 등록)
        else: 
            ws['A'+str(len(members)+2)] = text
            ws['C'+str(len(members)+2)] = '' # 사용 안 함
            ws['B'+str(len(members)+2)] = str(ctx.author.id)
            ws['E'+str(len(members)+2)] = 0
            ws['F'+str(len(members)+2)] = 0
            ws['G'+str(len(members)+2)] = int(time.strftime('%d', time.localtime(time.time())))   
            ws['A'+str(len(members)+3)] = 'endpoint'
            embed = discord.Embed(title="완료",
                        description = ctx.author.name+"님이 등록되었습니다.",
                        color=0xC8D7FF)
            embed.add_field(name="등록됨", value="```$포인트```로 보유 포인트를 확인해보세요.")
            await ctx.channel.send(embed=embed)
            print("[REGISTERED] "+ctx.author.name+"became member successfully. ("+time.strftime('%c', time.localtime(time.time()))+")")
            print("Minecraft Nickname: "+ctx.author.name+"/ Discord User ID: "+ctx.author.id+" ("+time.strftime('%c', time.localtime(time.time()))+")")
    db.save('database_example.xlsx')
    db.close()
   
# 봇 로그인
@bot.event
async def on_ready():
    # 봇 로그인 성공 로그
    print(f'{bot.user} successfully logined')
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="서버 CCTV"))
    await bot.change_presence(activity=discord.Game(name="<Activity>"))
    settings()
    db.close()

# 작동 테스트
@bot.command(name="test", aliases=["테스트", "Test"])
async def test(message):
    await message.channel.send('TEST')
    print(message.author.name+" testing bot.")

# 기본 $help 명령어 삭제
bot.remove_command('help')

# $help 명령어 재생성
@bot.group(invoke_without_command = True)
async def help(ctx):
    embed = discord.Embed(title="명령어 도움말",
                         description="디스코드 서버 내 봇 명령어 도움말입니다.\n$ 을 앞에 붙여 명령어를 입력할 수 있습니다\n```(예: $help, $help 서버)```",
                         color=0xC8D7FF)
    embed.add_field(name="📣 정보 (Info)", value="```$help``` ```$서버``` ```$문의```", inline="false")
    embed.add_field(name=":coin: 포인트 (Point)", value="```$포인트``` ```$등록``` ```$출석```")
    embed.add_field(name="🎮 게임 (Game)", value="```$홀짝``` ```$업다운``` ('$help 홀짝', '$help 업다운' 사용 불가능)", inline="false")
    embed.add_field(name="(추가)", value="본 디스코드 봇은 개발 단계이므로 오류 발생 시 문의해주세요", inline="false")
    await ctx.channel.send(embed=embed)

# $help 서버
@help.command()
async def 서버(ctx):
    embed = discord.Embed(title="$서버",
                             description="마인크래프트 서버 정보입니다.",
                             color=0xC8D7FF)
    embed.add_field(name="> 대체", value="server, ㄴㄷㄱㅍㄷㄱ, tjqj, 주소, wnth, address", inline="false")
    await ctx.channel.send(embed=embed)
# $help 문의
@help.command()
async def 문의(ctx):
    embed = discord.Embed(title="$문의",
                             description="봇 제작자 정보와 문의에 대한 안내입니다.",
                             color=0xC8D7FF)
    embed.add_field(name="", value="")
    await ctx.channel.send(embed=embed)
# $help 포인트
@help.command()
async def 포인트(ctx):
    embed = discord.Embed(title="$포인트",
                             description="자신의 포인트 보유량을 확인할 수 있습니다.",
                             color=0xC8D7FF)
    embed.add_field(name="> 대체", value="point", inline="false")
    await ctx.channel.send(embed=embed)
# $help 등록
@help.command()
async def 등록(ctx):
    embed = discord.Embed(title="$등록",
                             description="봇 서버에 자신의 정보를 저장합니다.",
                             color=0xC8D7FF)
    embed.add_field(name="> 형식", value="```$등록 <자신의 마인크래프트 닉네임>```\n닉네임을 정확히 입력해주세요.\nJE로 접속한 적이 있다면 반드시 JE 닉네임을 입력하고, BE로만 접속한다면 닉네임 앞에 .(온점)을 꼭 붙여주세요.", inline="false")
    await ctx.channel.send(embed=embed)
# $help help
@help.command()
async def help(ctx):
    embed = discord.Embed(title="$help",
                             description="도움말 관련 명령어",
                             color=0xC8D7FF)
    embed.add_field(name="> 대체", value="info, 안내, 헬프, 도움말, 도움", inline="false")
    embed.add_field(name="> 형식", value="```$help``` ```$help 서버```", inline="false")
    await ctx.channel.send(embed=embed)
# $help 홀짝
# 작동이 안 되는데 해결법을 아직 찾지 못했음..
'''@help.command()
async def 홀짝(ctx):
    embed = discord.Embed(title="$홀짝",
                             description="홀짝 게임 안내입니다.",
                             color=0xC8D7FF)
    embed.add_field(name="> 대체", value="dice, 다이스, ghfWkr, ekdltm, 얓ㄷ", inline="false")
    embed.add_field(name="> 형식", value="```$홀짝 <배팅할 포인트>````", inline="false")
    embed.add_field(name="> 방법", value="주사위의 눈이 홀수인지 짝수인지 맞추면 포인트를 얻고, 틀리면 포인트를 잃습니다.", inline="false")
    await ctx.channel.send(embed=embed)
# $help 업다운
@help.command()
async def 업다운(ctx):
    embed = discord.Embed(title="$업다운",
                             description="업다운 게임 안내입니다.",
                             color=0xC8D7FF)
    embed.add_field(name="> 대체", value="updown, djqekdns, ㅕㅔ애주")
    embed.add_field(name="> 형식", value="```$업다운 <배팅할 포인트>````", inline="false")
    embed.add_field(name="> 방법", value="임의의 수가 주어진 숫자보다 큰지 작은지 맞추면 포인트를 얻고, 틀리면 포인트를 잃습니다.", inline="false")
    await ctx.channel.send(embed=embed)
'''
# 서버 안내
@bot.command(name="서버", aliases=["server", "ㄴㄷㄱㅍㄷㄱ", "tjqj", "주소", "wnth", "address"])
async def server(ctx):
   embed = discord.Embed(title="서버 안내",
                         description = "*** 마인크래프트 서버입니다.",
                         color=0xC8D7FF)
   embed.add_field(name="> 서버 주소", value="***.***.**.**")
   embed.add_field(name="> 버전", value="1.20.2(JE) / 1.20.4(BE)")
   embed.add_field(name="> 추가 정보", value="[웹사이트](http://*****.***.**)")
   await ctx.channel.send(embed=embed)

# 포인트 확인
@bot.command(name="포인트", aliases=["point"])
async def point(ctx):
    settings()
    # 디스코드, 마인크래프트 모두 등록된 경우 (포인트 확인)
    if str(ctx.author.id) in members_id:
        embed = discord.Embed(title="포인트 정보",
                         description = ctx.author.name+"님의 포인트 정보입니다.",
                         color=0xC8D7FF)
        embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
        await ctx.channel.send(embed=embed)
    # 마인크래프트, 디스코드 아이디 등록 안 된 경우 (오류, 등록 권고)
    elif str(ctx.author.id) not in members_id:
        embed = discord.Embed(title="오류",
                         description = "사용자 오류가 발생했습니다.",
                         color=0xC8D7FF)
        embed.add_field(name="등록되지 않은 사용자", value="```$등록```을 통해 등록하세요\n```$등록 <마인크래프트 닉네임>\n- JE로 접속한 적 있다면 JE닉네임 정확히 입력\n- BE로만 접속한 경우 닉네임 앞에 온점(.) 반드시 표시\n\n등록 후에도 오류 발생 시 문의하세요```")
        await ctx.channel.send(embed=embed)
    db.save('database_example.xlsx')
    db.close()

# 문의
@bot.command(name="문의", aliases=["contact", "ansdml", "채ㅜㅅㅁㅊㅅ"])
async def 문의(ctx):
    embed = discord.Embed(title="문의",
                         description = "본 디스코드 봇은 개발 단계로 여러 가지 오류가 발생할 수 있습니다.",
                         color=0xC8D7FF)
    embed.add_field(name="> 오류 문의", value="고간디(kogandhi05)", inline="false")
    embed.add_field(name="> 이메일", value="hyungin0505@naver.com")
    embed.add_field(name="> 소스 코드", value="https://github.com/hyungin0505/MinecraftServer-DiscordBOT")
    await ctx.channel.send(embed=embed)

# 출석 체크
@bot.command(name="출석", aliases=["attend", "Attend", "cnftjr"])
async def 출석(ctx):
    settings()
    # 디스코드 등록된 경우
    if str(ctx.author.id) in members_id:
        # 출석 가능한 경우 (출석 보상 지급)
        if int(ws['G'+str(members_id.index(str(ctx.author.id))+2)].value) <= int(time.strftime('%d', time.localtime(time.time()))):
            bonus = random.randint(150,200)
        
            ws['E'+str(members_id.index(str(ctx.author.id))+2)] = int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) + bonus
            embed = discord.Embed(title="출석",
                         description = ctx.author.name+"님이 출석하였습니다.",
                         color=0xC8D7FF)
            embed.add_field(name="출석 보상이 지급됩니다.", value="", inline="false")
            embed.add_field(name="> 포인트 보상", value=bonus)
            embed.add_field(name="> 보유 포인트: ", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
            ch=bot.get_channel(12345)
            await ch.send("list")
            message_l =[]
            time.sleep(1.5)
            messages = [message async for message in ch.history(limit=4)]
            for message in messages:
                message_l.append(message.content)
            print(' '.join(message_l).split())
            print(str(ws['A'+str(members_id.index(str(ctx.author.id))+2)].value) + str(ws['A'+str(members_id.index(str(ctx.author.id))+2)].value)+"'" + str(ws['A'+str(members_id.index(str(ctx.author.id))+2)].value)+",")
            # 마인크래프트 접속된 경우 (출석 아이템 보상 지급)
            if str(ws['A'+str(members_id.index(str(ctx.author.id))+2)].value) in ' '.join(message_l).split() or str(ws['A'+str(members_id.index(str(ctx.author.id))+2)].value)+"'" in ' '.join(message_l).split() or str(ws['A'+str(members_id.index(str(ctx.author.id))+2)].value)+"," in ' '.join(message_l).split():
                tn = random.randint(1,4)
                await ch.send("give "+ws['A'+str(members_id.index(str(ctx.author.id))+2)].value+" minecraft:diamond "+str(tn))
                embed.add_field(name="> 아이템 보상", value="보상으로 다이아몬드 "+str(tn)+"개가 지급되었습니다.")
            # 마인크래프트 접속 안 된 경우 (출석 아이템 보상 미지급, 추가 포인트 지급)
            else:
                embed.add_field(name="> 아이템 보상", value="서버 접속이 확인되지 않아 추가 보너스 포인트만 지급되었습니다.")
                ws['E'+str(members_id.index(str(ctx.author.id))+2)] = int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) + bonus
            await ctx.channel.send(embed=embed)
            # 데이터베이스 출석 가능 날짜 업데이트
            # 1,3,5,7,9,11월인 경우
            if int(time.strftime('%m', time.localtime(time.time()))) == 1 or 3 or 5 or 7 or 9 or 11:
                # 31일인 경우
                if int(time.strftime('%d', time.localtime(time.time()))) == 31:
                    ws['G'+str(members_id.index(str(ctx.author.id))+2)] = 1
                else: 
                    ws['G'+str(members_id.index(str(ctx.author.id))+2)] = int(time.strftime('%d', time.localtime(time.time()))) + 1
            # 4,6,8,10,12월인 경우
            elif int(time.strftime('%m', time.localtime(time.time()))) == 4 or 6 or 8 or 10 or 12:
                # 30일인 경우
                if int(time.strftime('%d', time.localtime(time.time()))) == 30:
                    ws['G'+str(members_id.index(str(ctx.author.id))+2)] = 1
                else: 
                    ws['G'+str(members_id.index(str(ctx.author.id))+2)] = int(time.strftime('%d', time.localtime(time.time()))) + 1
            # 2월인 경우
            else:
                # 30일인 경우
                if int(time.strftime('%d', time.localtime(time.time()))) == 29:
                    ws['G'+str(members_id.index(str(ctx.author.id))+2)] = 1
                else: 
                    ws['G'+str(members_id.index(str(ctx.author.id))+2)] = int(time.strftime('%d', time.localtime(time.time()))) + 1
        # 출석 불가능한 경우
        else:
            embed = discord.Embed(title="출석",
                         description = "출석은 하루에 한 번만 가능합니다.",
                         color=0xC8D7FF)
            embed.add_field(name="내일 다시 시도해주세요.", value="")
            await ctx.channel.send(embed=embed)
    # 디스코드 등록 안 된 경우
    else: 
        embed = discord.Embed(title="오류",
                         description = "출석 오류가 발생했습니다.",
                         color=0xC8D7FF)
        embed.add_field(name="등록되지 않은 사용자", value="```$등록```을 통해 등록하세요\n```$등록 <마인크래프트 닉네임>\n- JE로 접속한 적 있다면 JE닉네임 정확히 입력\n- BE로만 접속한 경우 닉네임 앞에 온점(.) 반드시 표시\n\n등록 후에도 오류 발생 시 문의하세요```")
        await ctx.channel.send(embed=embed)
    db.save('database_example.xlsx')
    db.close()

#홀짝 게임
@bot.command(name="홀짝", aliases=["dice", "다이스", "ghfWkr", "ekdltm", "얓ㄷ"])
async def 홀짝(ctx, text: int):
    settings()
    # 등록된 사용자인 경우 (게임 시작)
    if str(ctx.author.id) in members_id:
        # 400이하 포인트 배팅 시 (게임 시작)
        if int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) >= int(text) and int(text) <= 400:
            dice = random.randint(1,6)
            embed = discord.Embed(title="홀수, 짝수 맞추기 게임",
                                    description="선택한 뒤에 어떤 수가 나왔는지 알려드립니다.",
                                    colour=0xC8D7FF)
            embed.add_field(name="> 주사위의 눈", value="???")
            embed.add_field(name="> 홀수", value="🔴")
            embed.add_field(name="짝수", value="🔵")
            msg = await ctx.channel.send(embed=embed)
            await msg.add_reaction("🔴")
            await msg.add_reaction("🔵")
            try:
                def check(reaction, user):
                    return str(reaction) in ['🔴','🔵'] and \
                    user == ctx.author and reaction.message.id == msg.id
                reaction, user = await bot.wait_for('reaction_add', check=check)
                if (str(reaction) == "🔴" and dice % 2 == 1) or \
                    (str(reaction) == "🔵" and dice % 2 == 0):
                        ws['E'+str(members_id.index(str(ctx.author.id))+2)] = int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) + int(text)
                        embed = discord.Embed(title="홀수, 짝수 맞추기 게임",
                                                description="정답입니다!!")
                else:
                    ws['E'+str(members_id.index(str(ctx.author.id))+2)] = int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) - int(text)
                    embed = discord.Embed(title="홀수, 짝수 맞추기 게임",
                                            description="틀렸습니다.. 다시 시도해보세요")
                
                embed.add_field(name="> 주사위의 눈", value=str(dice))
                embed.add_field(name="> 홀수", value="🔴")
                embed.add_field(name="> 짝수", value="🔵")
                embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
                await msg.clear_reactions()
                await msg.edit(embed=embed)
            except: pass
        # 포인트 부족 시
        elif int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) < int(text):
            embed = discord.Embed(title="오류",
                                    description="게임 오류가 발생했습니다.",
                                    colour=0xC8D7FF)
            embed.add_field(name="> 포인트 부족", value = '포인트가 부족합니다')
            embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
            msg = await ctx.channel.send(embed=embed)
        # 포인트 400 초과 배팅할 경우
        elif int(text) > 400:
            embed = discord.Embed(title="오류",
                                    description="게임 오류가 발생했습니다.",
                                    colour=0xC8D7FF)
            embed.add_field(name="> 도박 중독", value = '최대 400포인트까지 배팅할 수 있습니다')
            embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
            msg = await ctx.channel.send(embed=embed)
    # 등록 안 된 사용자일 경우 (게임 시작X, 오류 메세지)
    else:
        embed = discord.Embed(title="오류",
                         description = "게임 오류가 발생했습니다.",
                         color=0xC8D7FF)
        embed.add_field(name="등록되지 않은 사용자", value="```$등록```을 통해 등록하세요\n```$등록 <마인크래프트 닉네임>\n- JE로 접속한 적 있다면 JE닉네임 정확히 입력\n- BE로만 접속한 경우 닉네임 앞에 온점(.) 반드시 표시\n\n등록 후에도 오류 발생 시 문의하세요```")
        await ctx.channel.send(embed=embed)
    db.save('database_example.xlsx')
    db.close()
# 홀짝 게임 오류
@홀짝.error
async def game_error(ctx, error):
    # 배팅 금액 입력 안 함
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="오류",
                                description="게임 오류가 발생했습니다.",
                                colour=0xC8D7FF)
        embed.add_field(name="> 배팅할 금액을 입력해주세요.", value = '```$홀짝 <배팅할 금액>```')
        await ctx.channel.send(embed=embed)
    # 배팅 금액 숫자로 입력 안 함
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="오류",
                                description="게임 오류가 발생했습니다.",
                                colour=0xC8D7FF)
        embed.add_field(name="> 배팅할 금액은 숫자로 입력해주세요.", value = '```$홀짝 <배팅할 금액>```')
        await ctx.channel.send(embed=embed)

# 업다운 게임
@bot.command(name="업다운", aliases=["updown", "djqekdns", "ㅕㅔ애주"])
async def 업다운(ctx, text:int):
    settings()
    # 등록된 사용자일 경우 (게임 시작)
    if str(ctx.author.id) in members_id:
        # 400이하 포인트 배팅 시 (게임 시작)
        if int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) >= int(text) and int(text) <= 400:
            updown = random.randint(1,100)
            givenum = random.randint(1,100)
            embed = discord.Embed(title="업다운 게임",
                                    description="임의의 숫자가 주어진 숫자보다 큰지 맞춰보세요",
                                    colour=0xC8D7FF)
            embed.add_field(name="> 주어진 숫자", value = givenum)
            embed.add_field(name="> UP", value="🔴")
            embed.add_field(name="> DOWN", value="🔵")
            msg = await ctx.channel.send(embed=embed)
            await msg.add_reaction("🔴")
            await msg.add_reaction("🔵")
            try:
                def check(reaction, user):
                    return str(reaction) in ['🔴','🔵']and \
                    user == ctx.author and reaction.message.id == msg.id
                reaction, user = await bot.wait_for('reaction_add', check=check)
                if (str(reaction) == "🔴" and updown > givenum) or \
                (str(reaction) == "🔵" and updown < givenum):
                    ws['E'+str(members_id.index(str(ctx.author.id))+2)] = int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) + int(text)
                    embed = discord.Embed(title="업다운 게임", 
                                        description="정답입니다!!")
                else:
                    ws['E'+str(members_id.index(str(ctx.author.id))+2)] = int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) - int(text)
                    embed = discord.Embed(title="업다운 게임", 
                                        description="틀렸습니다")
                embed.add_field(name="> 주어진 숫자", value=str(updown))
                embed.add_field(name="> UP", value="🔴")
                embed.add_field(name="> DOWN", value="🔵")
                embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
                await msg.clear_reactions()
                await msg.edit(embed=embed)
            except: pass
        # 포인트 부족 시
        elif int(ws['E'+str(members_id.index(str(ctx.author.id))+2)].value) < int(text):
            embed = discord.Embed(title="오류",
                                    description="게임 오류가 발생했습니다.",
                                    colour=0xC8D7FF)
            embed.add_field(name="> 포인트 부족", value = '포인트가 부족합니다')
            embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
            msg = await ctx.channel.send(embed=embed)
        # 포인트 400초과 배팅 시
        elif int(text) > 400:
            embed = discord.Embed(title="오류",
                                    description="게임 오류가 발생했습니다.",
                                    colour=0xC8D7FF)
            embed.add_field(name="> 도박 중독", value = '최대 400포인트까지 배팅할 수 있습니다')
            embed.add_field(name="> 보유 포인트", value=ws['E'+str(members_id.index(str(ctx.author.id))+2)].value)
            msg = await ctx.channel.send(embed=embed)
    # 등록 안 된 사용자일 경우 (게임 시작X, 오류 메세지)
    else:
        embed = discord.Embed(title="오류",
                         description = "게임 오류가 발생했습니다.",
                         color=0xC8D7FF)
        embed.add_field(name="등록되지 않은 사용자", value="```$등록```을 통해 등록하세요\n```$등록 <마인크래프트 닉네임>\n- JE로 접속한 적 있다면 JE닉네임 정확히 입력\n- BE로만 접속한 경우 닉네임 앞에 온점(.) 반드시 표시\n\n등록 후에도 오류 발생 시 문의하세요```")
        await ctx.channel.send(embed=embed)
    db.save('database_example.xlsx')
    db.close()
# 업다운 게임 오류
@업다운.error
async def game_error(ctx, error):
    # 배팅 금액 입력 안 함
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="오류",
                                description="게임 오류가 발생했습니다.",
                                colour=0xC8D7FF)
        embed.add_field(name="> 배팅할 금액을 입력해주세요.", value = '```$업다운 <배팅할 금액>```')
        await ctx.channel.send(embed=embed)
    # 배팅 금액 숫자로 입력 안 함
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="오류",
                                description="게임 오류가 발생했습니다.",
                                colour=0xC8D7FF)
        embed.add_field(name="> 배팅할 금액은 숫자로 입력해주세요.", value = '```$업다운 <배팅할 금액>```')
        await ctx.channel.send(embed=embed)

# 봇 작동
bot.run(TOKEN)