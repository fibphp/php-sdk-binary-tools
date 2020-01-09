<?php

namespace SDK\Build\Dependency;

use SDK\{Config, Exception, FileOps};

class Package
{
	use FileOps;

	protected $name;
	protected $series;
	protected $fetcher;
	protected $filepath;

	public function __construct(string $name, Series $series, Fetcher $fetcher)
	{/*{{{*/
		$this->name = $name;
		$this->series = $series;
		$this->fetcher = $fetcher;
	}/*}}}*/

	public function getUri() : string
	{/*{{{*/
		$base = Config::getDepsBaseUri();
		$branch_data = Config::getCurrentBranchData();
		$arch = $this->series->getArch();

		return "$base/{$branch_data['crt']}/$arch/{$this->name}";
	}/*}}}*/

	public function retrieve(string $path) : void
	{/*{{{*/
		$this->filepath = $path . DIRECTORY_SEPARATOR . $this->name;

        $preg = <<<'EOT'
        \.tmp([\\\w]+\\packs\\)
        EOT;
        $preg = trim($preg);

        $bakfile = preg_replace("/$preg/", ".tmp\\", $this->filepath);

        $url = $this->getUri();
        if(is_file($bakfile)){
        	$_url = $this->fetcher->buildUri($url);
            echo "\n use bak file {$bakfile} with: \n\t{$_url}\n";
            copy($bakfile, $this->filepath);
        } else {
            $cont = $this->fetcher->getByUri($url);

            $fd = fopen($this->filepath, "wb");
            fwrite($fd, $cont);
            fclose($fd);
        }
        
	}/*}}}*/

	public function unpack(string $path) : void
	{/*{{{*/
		if (!$this->filepath || !file_exists($this->filepath)) {
			throw new Exception("Invalid filepath '{$this->filepath}'");
		}

		$this->unzip($this->filepath, $path);
	}/*}}}*/

	public function cleanup() : void
	{/*{{{*/
        $preg = <<<'EOT'
        \.tmp([\\\w]+\\packs\\)
        EOT;
        $preg = trim($preg);

        $bakfile = preg_replace("/$preg/", ".tmp\\", $this->filepath);

        if(!is_file($bakfile)){
            copy($this->filepath, $bakfile);
            echo "\n try bak file to: \n\t{$bakfile}\n";
        }

		unlink($this->filepath);		
	}/*}}}*/
}

/*
 * Local variables:
 * tab-width: 4
 * c-basic-offset: 4
 * End:
 * vim600: sw=4 ts=4 fdm=marker
 * vim<600: sw=4 ts=4
 */
