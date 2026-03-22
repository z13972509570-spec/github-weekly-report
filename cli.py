import click

@click.command()
def run():
    """Run the tool"""
    click.echo("Running...")
    click.echo("Done!")

if __name__ == "__main__":
    run()
