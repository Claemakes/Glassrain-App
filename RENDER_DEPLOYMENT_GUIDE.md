# GlassRain Deployment Guide for Render

## Overview

This guide provides step-by-step instructions for deploying GlassRain on [Render](https://render.com), a modern cloud platform. Render offers a reliable environment for hosting web applications with built-in PostgreSQL database support.

## Prerequisites

Before deploying, ensure you have:

1. A [Render account](https://dashboard.render.com/register)
2. A [GitHub account](https://github.com/join) for source code hosting
3. A valid [Mapbox API key](https://account.mapbox.com/) for geocoding and map visualization
4. A copy of the GlassRain export package (`glassrain_render_package_final.zip`)

## Step 1: Prepare Your GitHub Repository

1. Create a new GitHub repository:
   - Go to [GitHub](https://github.com)
   - Click the "+" icon in the top right and select "New repository"
   - Name your repository (e.g., "glassrain-deployment")
   - Set it to "Public" or "Private" based on your needs
   - Click "Create repository"

2. Upload the GlassRain export package:
   - Extract the contents of `glassrain_render_package_final.zip` to your local machine
   - Use GitHub Desktop or git commands to commit and push the files to your repository
   - Verify all files are properly uploaded by checking your repository on GitHub

## Step 2: Set Up a PostgreSQL Database on Render

1. Log in to your [Render Dashboard](https://dashboard.render.com/)

2. Create a new PostgreSQL database:
   - Click "New +" and select "PostgreSQL"
   - Enter a name (e.g., "glassrain-db")
   - Keep the default PostgreSQL version
   - Choose a region closest to your target users
   - Select an appropriate plan based on your needs
   - Click "Create Database"

3. Wait for the database to be provisioned (this may take a few minutes)

4. Once created, note the following details from the database page:
   - Internal Database URL
   - External Database URL
   - Username
   - Password

## Step 3: Deploy GlassRain Web Service

1. From your Render Dashboard:
   - Click "New +" and select "Web Service"

2. Connect your GitHub repository:
   - Select "GitHub" as the deployment method
   - Connect your GitHub account if not already connected
   - Select the repository you created in Step 1
   - Click "Connect"

3. Configure the web service:
   - **Name**: Enter a name for your service (e.g., "glassrain")
   - **Environment**: Select "Python 3"
   - **Region**: Choose the same region as your database for optimal performance
   - **Branch**: Select "main" (or your preferred branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`

4. Set up environment variables (click "Advanced" to expand this section):
   - `DATABASE_URL`: Paste the External Database URL from Step 2
   - `FLASK_SECRET_KEY`: Generate a random string (can use `openssl rand -hex 24`)
   - `MAPBOX_API_KEY`: Enter your Mapbox API key
   - `FLASK_ENV`: Set to `production`
   - `PORT`: Set to `10000` (Render will override this, but it's needed for local testing)

5. Select a plan type based on your needs

6. Click "Create Web Service"

7. Wait for the deployment to complete (this may take a few minutes)

## Step 4: Initialize the Database

1. After deployment, your database will be empty. To initialize it with the required tables and seed data:

   - On the Render dashboard, go to your web service
   - Click on the "Shell" tab
   - In the shell, run:
     ```
     python initialize_db.py
     ```
   - Wait for the script to complete (you should see "Database initialization complete!")

2. Verify the database initialization:
   - In the shell, run:
     ```
     python check_db.py
     ```
   - You should see a list of tables and sample data confirming the initialization succeeded

## Step 5: Configure Custom Domain (Optional)

1. If you have a custom domain you'd like to use:
   - Go to your web service on the Render dashboard
   - Click "Settings" and then "Custom Domain"
   - Click "Add Custom Domain"
   - Enter your domain name
   - Follow the instructions to update your DNS settings
   - Wait for DNS propagation (may take up to 48 hours)

## Step 6: Final Verification

1. Once deployed, your GlassRain instance is available at the URL provided by Render (e.g., `https://glassrain.onrender.com`)

2. Verify the deployment by:
   - Visiting the home page
   - Testing the address entry form
   - Checking that services load correctly
   - Verifying AR functionality works
   - Testing store and product integrations

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify the `DATABASE_URL` environment variable is correctly set
2. Check that your IP is allowed in the database's access control settings
3. Ensure the database is fully provisioned and running

### Application Errors

If the application fails to start:

1. Check the logs in the Render dashboard for specific error messages
2. Verify all required environment variables are set
3. Ensure the `gunicorn` start command is correct
4. Check that `requirements.txt` includes all necessary dependencies

### Mapbox Integration Issues

If maps or geocoding aren't working:

1. Verify your Mapbox API key is correct and has the necessary permissions
2. Check that the key is properly set in the `MAPBOX_API_KEY` environment variable
3. Confirm there are no JavaScript console errors in the browser

## Scaling and Optimization

### Scaling Options

As your user base grows, you may need to scale your deployment:

1. **Database Scaling**:
   - Upgrade to a larger database plan on Render
   - Monitor database performance and increase resources as needed

2. **Web Service Scaling**:
   - Increase the number of instances for your web service
   - Upgrade to a more powerful service plan

### Performance Optimization

For optimal performance:

1. Enable Render's built-in CDN for static assets
2. Consider implementing Redis caching (available as a Render service)
3. Optimize image assets with compression
4. Monitor your service's metrics to identify bottlenecks

## Maintenance

### Regular Updates

To keep your deployment secure and up to date:

1. Regularly update your GitHub repository with the latest GlassRain updates
2. Render will automatically redeploy your service when changes are pushed to your repository
3. Schedule regular database backups using Render's backup feature

### Monitoring

Use Render's built-in monitoring tools to:

1. Track CPU and memory usage
2. Monitor response times
3. Set up alerts for abnormal service behavior

## Support

For additional assistance with your Render deployment:

1. Consult [Render's documentation](https://render.com/docs)
2. Contact [Render support](https://render.com/support)
3. For GlassRain-specific issues, refer to the project documentation
