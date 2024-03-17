{
  description = "cursorgen is a fork of win2xcur that aims to preserve the image quality of the cursor.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
    devshell.url = "github:numtide/devshell";
  };

  outputs = {
    self,
    pre-commit-hooks-nix,
    ...
  } @ inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
      imports = [inputs.flake-parts.flakeModules.easyOverlay];
      perSystem = {
        config,
        system,
        pkgs,
        ...
      }: {
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          overlays = [
            inputs.devshell.overlays.default
          ];
        };
        devShells.default = pkgs.devshell.mkShell {
          imports = [(pkgs.devshell.importTOML ./devshell.toml)];
          packages = with pkgs; [
            (python3.withPackages (p:
              with p; [
                wand
                numpy
                pillow
                toml
                black
                flake8
                isort
                mypy
              ]))
          ];
        };
        formatter = pkgs.alejandra;
      };
    };
}
