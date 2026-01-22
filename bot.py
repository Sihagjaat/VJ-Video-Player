# VJ Video Player Bot - Updated with Adsterra Ads Integration
# YouTube: @Tech_VJ | Telegram: @VJ_Bots | GitHub: @VJBots

import sys
import glob
import asyncio
import logging
import logging.config
from pathlib import Path
from aiohttp import web
from pyrogram import Client, idle
from pyrogram.errors import FloodWait

# Import configurations
from info import *
from TechVJ.bot import TechVJBot
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ.server import web_server
from TechVJ.database import Database

# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

# Initialize database
db = Database(DATABASE_URI, SESSION)

class Bot(Client):
    """Main Bot Class"""
    
    def __init__(self):
        super().__init__(
            name="VJVideoPlayer",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        """Start the bot"""
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        self.id = me.id
        self.mention = me.mention
        
        # Start web server with ads integration
        app = web.Application(client_max_size=30000000)
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Bind to configured port
        bind_address = "0.0.0.0"
        port = PORT
        
        await web.TCPSite(runner, bind_address, port).start()
        
        # Set up routes with ads support
        routes = web.RouteTableDef()
        
        @routes.get("/", allow_head=True)
        async def root_route_handler(request):
            """Root route - Homepage"""
            return web.json_response({
                "status": "running",
                "bot": "VJ Video Player",
                "version": "2.0 with Ads"
            })
        
        @routes.get("/stream/{file_id}", allow_head=True)
        async def stream_handler(request):
            """Stream route - Main video player with ads"""
            try:
                file_id = request.match_info['file_id']
                
                # Get file info from database
                file_data = await db.get_file(file_id)
                
                if not file_data:
                    return web.Response(
                        text="<h1>File Not Found</h1><p>This file doesn't exist or has been deleted.</p>",
                        content_type='text/html',
                        status=404
                    )
                
                # Read HTML template (dl.html with ads)
                try:
                    with open('TechVJ/template/dl.html', 'r', encoding='utf-8') as f:
                        html_content = f.read()
                except FileNotFoundError:
                    return web.Response(
                        text="<h1>Template Error</h1><p>Template file not found.</p>",
                        content_type='text/html',
                        status=500
                    )
                
                # Replace placeholders with actual data
                html_content = html_content.replace(
                    'Sample Video File.mp4', 
                    file_data.get('file_name', 'Unknown')
                )
                html_content = html_content.replace(
                    'Loading...', 
                    get_readable_file_size(file_data.get('file_size', 0))
                )
                html_content = html_content.replace(
                    'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                    f'{STREAM_LINK}download/{file_id}'
                )
                
                # Update view count
                await db.increment_views(file_id)
                current_views = file_data.get('views', 0) + 1
                html_content = html_content.replace('id="viewCount">0', f'id="viewCount">{current_views}')
                
                return web.Response(
                    text=html_content,
                    content_type='text/html'
                )
                
            except Exception as e:
                logging.error(f"Stream handler error: {e}")
                return web.Response(
                    text=f"<h1>Error</h1><p>An error occurred: {str(e)}</p>",
                    content_type='text/html',
                    status=500
                )
        
        @routes.get("/quality", allow_head=True)
        async def quality_handler(request):
            """Quality selection page with ads"""
            try:
                file_id = request.query.get('id', '')
                
                if not file_id:
                    return web.Response(
                        text="<h1>Error</h1><p>File ID is required.</p>",
                        content_type='text/html',
                        status=400
                    )
                
                # Get file info
                file_data = await db.get_file(file_id)
                
                if not file_data:
                    return web.Response(
                        text="<h1>File Not Found</h1>",
                        content_type='text/html',
                        status=404
                    )
                
                # Read quality template (req.html with ads)
                try:
                    with open('TechVJ/template/req.html', 'r', encoding='utf-8') as f:
                        html_content = f.read()
                except FileNotFoundError:
                    # Fallback to direct stream if req.html not found
                    return web.HTTPFound(f'/stream/{file_id}')
                
                # Replace placeholders
                html_content = html_content.replace(
                    'Sample Video.mp4',
                    file_data.get('file_name', 'Unknown')
                )
                html_content = html_content.replace(
                    '245 MB',
                    get_readable_file_size(file_data.get('file_size', 0))
                )
                
                return web.Response(
                    text=html_content,
                    content_type='text/html'
                )
                
            except Exception as e:
                logging.error(f"Quality handler error: {e}")
                return web.HTTPFound(f'/stream/{file_id}')
        
        @routes.get("/download/{file_id}", allow_head=True)
        async def download_handler(request):
            """Download/stream file handler"""
            try:
                file_id = request.match_info['file_id']
                
                # Get file from Telegram
                file_data = await db.get_file(file_id)
                
                if not file_data:
                    raise FIleNotFound
                
                # Get file from Telegram
                file = await self.get_messages(
                    chat_id=LOG_CHANNEL,
                    message_ids=int(file_data.get('message_id'))
                )
                
                if not file.media:
                    raise FIleNotFound
                
                # Stream the file
                media = file.document or file.video or file.audio
                
                file_size = media.file_size
                file_name = media.file_name
                mime_type = media.mime_type
                
                # Handle range requests for video streaming
                range_header = request.headers.get('Range', None)
                
                if range_header:
                    # Parse range header
                    from_bytes, until_bytes = 0, file_size - 1
                    match = re.search(r'bytes=(\d+)-(\d*)', range_header)
                    
                    if match:
                        from_bytes = int(match.group(1))
                        if match.group(2):
                            until_bytes = int(match.group(2))
                    
                    # Stream specific range
                    chunk_size = 1024 * 1024  # 1MB chunks
                    offset = from_bytes
                    
                    headers = {
                        'Content-Type': mime_type,
                        'Content-Range': f'bytes {from_bytes}-{until_bytes}/{file_size}',
                        'Content-Length': str(until_bytes - from_bytes + 1),
                        'Accept-Ranges': 'bytes',
                    }
                    
                    response = web.StreamResponse(
                        status=206,
                        reason='Partial Content',
                        headers=headers
                    )
                    
                    await response.prepare(request)
                    
                    # Stream file
                    async for chunk in self.stream_media(
                        file,
                        offset=offset,
                        limit=until_bytes - from_bytes + 1
                    ):
                        await response.write(chunk)
                    
                    return response
                
                else:
                    # Full file download
                    headers = {
                        'Content-Type': mime_type,
                        'Content-Length': str(file_size),
                        'Content-Disposition': f'inline; filename="{file_name}"'
                    }
                    
                    response = web.StreamResponse(
                        status=200,
                        reason='OK',
                        headers=headers
                    )
                    
                    await response.prepare(request)
                    
                    # Stream full file
                    async for chunk in self.stream_media(file):
                        await response.write(chunk)
                    
                    return response
                
            except FIleNotFound:
                return web.Response(
                    text="File Not Found",
                    status=404
                )
            except Exception as e:
                logging.error(f"Download error: {e}")
                return web.Response(
                    text=f"Error: {str(e)}",
                    status=500
                )
        
        # Add routes to app
        app.add_routes(routes)
        
        logging.info(f"✅ Bot Started Successfully!")
        logging.info(f"👤 Bot: {me.first_name}")
        logging.info(f"🆔 Username: @{me.username}")
        logging.info(f"🌐 Server: http://0.0.0.0:{port}")
        logging.info(f"🔗 Stream Link: {STREAM_LINK}")
        logging.info(f"💰 Ads: Adsterra Integrated")
        
        # Send start message to log channel
        try:
            await self.send_message(
                chat_id=LOG_CHANNEL,
                text=f"✅ **Bot Started Successfully!**\n\n"
                     f"👤 Bot: {me.first_name}\n"
                     f"🆔 Username: @{me.username}\n"
                     f"🌐 Server: Running on port {port}\n"
                     f"💰 Ads: Adsterra Integrated"
            )
        except Exception as e:
            logging.warning(f"Could not send start message: {e}")

    async def stop(self, *args):
        """Stop the bot"""
        await super().stop()
        logging.info("Bot Stopped!")


def get_readable_file_size(size_in_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_in_bytes is None:
        return "0 B"
    
    SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    size = float(size_in_bytes)
    
    while size >= 1024 and index < len(SIZE_UNITS) - 1:
        size /= 1024
        index += 1
    
    return f"{size:.2f} {SIZE_UNITS[index]}"


# Multi-client support
if MULTI_CLIENT:
    logging.info("Multi-client mode enabled")
    apps = [Bot()]
    
    # Add additional clients
    for i in range(1, 50):  # Support up to 50 clients
        token_var = f'MULTI_TOKEN{i}'
        token = globals().get(token_var)
        
        if token:
            try:
                apps.append(
                    Client(
                        name=f"VJVideoPlayer{i}",
                        api_id=API_ID,
                        api_hash=API_HASH,
                        bot_token=token,
                        workers=200,
                        plugins={"root": "plugins"},
                        sleep_threshold=15,
                    )
                )
                logging.info(f"✅ Multi-client {i} added")
            except Exception as e:
                logging.error(f"❌ Multi-client {i} failed: {e}")
        else:
            break
else:
    apps = [Bot()]
    logging.info("Single client mode")

# Main execution
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    try:
        # Start all clients
        for app in apps:
            loop.run_until_complete(app.start())
        
        # Keep running
        loop.run_until_complete(idle())
        
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot error: {e}")
    finally:
        # Stop all clients
        for app in apps:
            loop.run_until_complete(app.stop())
        
        loop.close()
        logging.info("Bot shutdown complete")
